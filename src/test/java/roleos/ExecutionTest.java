package roleos;

import static org.junit.jupiter.api.Assertions.*;

import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import org.junit.jupiter.api.*;

class ExecutionTest {
  static class MutableClock extends Clock {
    long now = Instant.parse("2026-10-07T08:00:00Z").toEpochMilli();

    public ZoneId getZone() {
      return ZoneOffset.UTC;
    }

    public Clock withZone(ZoneId zone) {
      return this;
    }

    public Instant instant() {
      return Instant.ofEpochMilli(now);
    }

    void advance(long ms) {
      now += ms;
    }
  }

  Database db;
  TerminalService service;
  MutableClock clock;
  Auth auth;
  static final String VIN = "DEMO0000000000001";

  static Map<String, String> tokens() {
    var map = new HashMap<String, String>();
    for (String n : List.of("ALPHA", "BETA", "READER", "OPERATOR", "ADMIN"))
      map.put("ROLEOS_" + n + "_TOKEN", "test-only-" + n + "-" + UUID.randomUUID());
    return map;
  }

  Map<String, String> env;

  @BeforeEach
  void before() {
    clock = new MutableClock();
    db = new Database("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=Oracle;DB_CLOSE_DELAY=-1");
    service = new TerminalService(db, clock);
    env = tokens();
    auth = new Auth(env);
  }

  Auth.Actor actor(String role) {
    return auth.authenticate("Bearer " + env.get("ROLEOS_" + role + "_TOKEN"));
  }

  com.fasterxml.jackson.databind.JsonNode event(
      String key, String type, String site, String location, int version, String vin) {
    return Json.read(
        Json.write(
            Map.of(
                "message_id",
                "transport-" + key,
                "event_key",
                key,
                "partner_id",
                "ALPHA",
                "site_id",
                site,
                "vin",
                vin,
                "event_type",
                type,
                "location",
                location,
                "event_at",
                clock.instant().toString(),
                "expected_version",
                version)));
  }

  TerminalService.Receipt arrival() {
    var r =
        service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("ALPHA"), "test");
    assertTrue(service.processOnce());
    return r;
  }

  long count(String table) {
    return TerminalService.number(
        Database.first(db.query("SELECT COUNT(*) AS n FROM " + table)), "n");
  }

  @Test
  void acceptedReceiptIsNotCommit() {
    var r =
        service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("ALPHA"), "test");
    assertEquals("RECEIVED", r.status());
    assertEquals(0, count("vehicles"));
  }

  @Test
  void atomicVehicleEventAuditAndOutboxCommit() {
    arrival();
    assertEquals(1, count("vehicles"));
    assertEquals(1, count("business_events"));
    assertEquals(1, count("audit_log"));
    assertEquals(1, count("outbox"));
    assertEquals("PROCESSED", db.query("SELECT status FROM messages").getFirst().get("status"));
  }

  @Test
  void duplicateTransportIdDoesNotDuplicateBusinessEffect() {
    var r = arrival();
    var n =
        (com.fasterxml.jackson.databind.node.ObjectNode)
            event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN);
    n.put("message_id", "another-transport");
    var duplicate = service.accept(n, actor("ALPHA"), "test");
    assertTrue(duplicate.duplicate());
    assertEquals(r.id(), duplicate.id());
    assertFalse(service.processOnce());
    assertEquals(1, count("business_events"));
    assertEquals(2, count("deliveries"));
  }

  @Test
  void changedPayloadWithSameKeyConflicts() {
    arrival();
    var error =
        assertThrows(
            ApiError.class,
            () ->
                service.accept(
                    event("A1", "ARRIVAL", "ZEE", "ZEE-A02", 0, VIN), actor("ALPHA"), "test"));
    assertEquals("IDEMPOTENCY_CONFLICT", error.code);
    assertEquals(1, count("messages"));
  }

  @Test
  void concurrentDuplicateRequestsRemainUnique() throws Exception {
    var n = event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN);
    try (var pool = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Callable<TerminalService.Receipt>>();
      for (int i = 0; i < 16; i++)
        tasks.add(() -> service.accept(n, actor("ALPHA"), "concurrency"));
      for (var f : pool.invokeAll(tasks)) assertNotNull(f.get());
    }
    service.processOnce();
    assertEquals(1, count("messages"));
    assertEquals(1, count("business_events"));
    assertEquals(16, count("deliveries"));
  }

  @Test
  void malformedJsonAndTrailingInputRejected() {
    assertThrows(ApiError.class, () -> Json.read("{broken"));
    assertThrows(ApiError.class, () -> Json.read("{} {}"));
  }

  @Test
  void fieldsTypesDatesAndUnknownKeysValidated() {
    var n =
        (com.fasterxml.jackson.databind.node.ObjectNode)
            event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN);
    n.put("expected_version", "0");
    assertThrows(ApiError.class, () -> service.accept(n, actor("ALPHA"), "test"));
    n.put("expected_version", 0);
    n.put("unexpected", "x");
    assertThrows(ApiError.class, () -> service.accept(n, actor("ALPHA"), "test"));
    n.remove("unexpected");
    n.put("event_at", "not-a-date");
    assertThrows(ApiError.class, () -> service.accept(n, actor("ALPHA"), "test"));
  }

  @Test
  void partnerCannotSpoofScope() {
    assertEquals(
        403,
        assertThrows(
                ApiError.class,
                () ->
                    service.accept(
                        event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("BETA"), "test"))
            .status);
  }

  @Test
  void unknownLocationRejectsWithoutPartialVehicleOrOutbox() {
    service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A-01", 0, VIN), actor("ALPHA"), "test");
    service.processOnce();
    assertEquals(
        "UNKNOWN_LOCATION",
        db.query("SELECT last_error FROM messages").getFirst().get("last_error"));
    assertEquals(0, count("vehicles"));
    assertEquals(0, count("outbox"));
  }

  @Test
  void mappingFixAndAuthorizedRedriveAreAudited() {
    assertThrows(
        ApiError.class,
        () -> service.controls(Json.read("{\"mapping_version\":2}"), actor("ADMIN"), "bad-type"));
    var r =
        service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A-01", 0, VIN), actor("ALPHA"), "test");
    service.processOnce();
    service.controls(Json.read("{\"mapping_version\":\"2\"}"), actor("ADMIN"), "chg");
    service.redrive(r.id(), actor("ADMIN"), "CHG-003 verified mapping", "chg");
    service.processOnce();
    assertEquals(1, count("vehicles"));
    assertEquals(3, count("audit_log"));
    assertThrows(
        ApiError.class, () -> service.redrive(r.id(), actor("ADMIN"), "cannot repeat", "test"));
  }

  @Test
  void transientFailureRetriesAndAttemptLimitDeadLetters() {
    service.controls(Json.read("{\"dependency_unavailable\":true}"), actor("ADMIN"), "test");
    service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("ALPHA"), "test");
    for (int i = 0; i < 5; i++) {
      assertTrue(service.processOnce());
      clock.advance(20_000);
    }
    assertEquals("DEAD_LETTER", db.query("SELECT status FROM messages").getFirst().get("status"));
    assertEquals(0, count("vehicles"));
  }

  @Test
  void dependencyRecoveryCommitsOnlyOnce() {
    service.controls(Json.read("{\"dependency_unavailable\":true}"), actor("ADMIN"), "test");
    service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("ALPHA"), "test");
    service.processOnce();
    service.controls(Json.read("{\"dependency_unavailable\":false}"), actor("ADMIN"), "test");
    clock.advance(2000);
    service.processOnce();
    assertEquals(1, count("business_events"));
  }

  @Test
  void pausedWorkerProducesHonestBacklogMetric() {
    service.controls(Json.read("{\"worker_paused\":true}"), actor("ADMIN"), "test");
    service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("ALPHA"), "test");
    clock.advance(90_000);
    assertFalse(service.processOnce());
    assertEquals(90L, service.metrics().get("oldest_pending_seconds"));
  }

  @Test
  void staleVersionAndOutOfOrderAreBusinessRejects() {
    arrival();
    clock.advance(1000);
    service.accept(event("M1", "MOVE", "ZEE", "ZEE-A02", 0, VIN), actor("ALPHA"), "test");
    service.processOnce();
    assertEquals(
        "VERSION_CONFLICT",
        db.query("SELECT last_error FROM messages WHERE event_key='M1'")
            .getFirst()
            .get("last_error"));
    clock.advance(-1000);
    service.accept(event("M2", "MOVE", "ZEE", "ZEE-A02", 1, VIN), actor("ALPHA"), "test");
    service.processOnce();
    assertEquals(
        "OUT_OF_ORDER",
        db.query("SELECT last_error FROM messages WHERE event_key='M2'")
            .getFirst()
            .get("last_error"));
  }

  @Test
  void safetyHoldBlocksDepartureAndReleaseRequiresDecision() {
    arrival();
    service.correct(
        VIN,
        Json.read(
            "{\"expected_version\":1,\"hold\":true,\"reason\":\"Physical verification pending\"}"),
        actor("OPERATOR"),
        "test",
        true);
    clock.advance(1000);
    service.accept(event("D1", "DEPARTURE", "ZEE", "ZEE-A01", 2, VIN), actor("ALPHA"), "test");
    service.processOnce();
    assertEquals(
        "HOLD_ACTIVE",
        db.query("SELECT last_error FROM messages WHERE event_key='D1'")
            .getFirst()
            .get("last_error"));
    assertThrows(
        ApiError.class,
        () ->
            service.correct(
                VIN,
                Json.read(
                    "{\"expected_version\":2,\"hold\":false,\"reason\":\"Verified\",\"decision_ref\":\"BUS-001\"}"),
                actor("OPERATOR"),
                "test",
                true));
    service.correct(
        VIN,
        Json.read(
            "{\"expected_version\":2,\"hold\":false,\"reason\":\"Verified\",\"decision_ref\":\"BUS-001\"}"),
        actor("ADMIN"),
        "test",
        true);
  }

  @Test
  void portalCorrectionHasAuthorizationConflictAndAudit() {
    arrival();
    var n =
        Json.read(
            "{\"expected_version\":1,\"location\":\"ZEE-A02\",\"reason\":\"Physical position"
                + " checked\"}");
    assertThrows(ApiError.class, () -> service.correct(VIN, n, actor("READER"), "test", false));
    assertEquals(
        2,
        TerminalService.number(
            service.correct(VIN, n, actor("OPERATOR"), "test", false), "version"));
    assertThrows(ApiError.class, () -> service.correct(VIN, n, actor("OPERATOR"), "test", false));
    assertEquals(2, count("audit_log"));
  }

  @Test
  void reportCountsVehiclesNotDeliveriesAndHandlesBothSites() {
    arrival();
    service.accept(
        event("A2", "ARRIVAL", "KAL", "KAL-B01", 0, "DEMO0000000000002"), actor("ALPHA"), "test");
    service.processOnce();
    service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("ALPHA"), "test");
    assertEquals(2, service.report(actor("READER")).size());
    assertEquals(0, service.report(actor("BETA")).size());
    assertEquals(2, count("vehicles"));
  }

  @Test
  void routerHandlesAuthRateSizeAndRecovery() {
    var router = new Router(service, auth, 2);
    assertEquals(401, router.handle("GET", "/api/vehicles", null, "", null).status());
    String bearer = "Bearer " + env.get("ROLEOS_READER_TOKEN");
    assertEquals(200, router.handle("GET", "/api/vehicles", bearer, "", null).status());
    assertEquals(200, router.handle("GET", "/api/vehicles", bearer, "", null).status());
    assertEquals(429, router.handle("GET", "/api/vehicles", bearer, "", null).status());
    clock.advance(60_000);
    assertEquals(
        413, router.handle("POST", "/api/messages", bearer, "x".repeat(17000), null).status());
  }

  @Test
  void lostAckDoesNotReplayBusinessMutation() throws Exception {
    arrival();
    service.controls(Json.read("{\"ack_timeout\":true}"), actor("ADMIN"), "test");
    String secret = "test-only-secret-with-enough-entropy";
    var server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
    var received = new HashSet<String>();
    server.createContext(
        "/ack",
        x -> {
          String p = new String(x.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
          assertTrue(
              MessageDigest.isEqual(
                  Worker.signature(secret, p).getBytes(StandardCharsets.UTF_8),
                  x.getRequestHeaders()
                      .getFirst("X-RoleOS-Signature")
                      .getBytes(StandardCharsets.UTF_8)));
          received.add(Json.read(p).get("ack_id").asText());
          x.sendResponseHeaders(200, -1);
          x.close();
        });
    server.start();
    try {
      var worker =
          new Worker(service, "http://127.0.0.1:" + server.getAddress().getPort() + "/ack", secret);
      worker.dispatchOnce();
      assertEquals("RETRY_WAIT", db.query("SELECT status FROM outbox").getFirst().get("status"));
      service.controls(Json.read("{\"ack_timeout\":false}"), actor("ADMIN"), "test");
      clock.advance(2000);
      worker.dispatchOnce();
      assertEquals("SENT", db.query("SELECT status FROM outbox").getFirst().get("status"));
      assertEquals(1, count("business_events"));
      assertEquals(1, received.size());
    } finally {
      server.stop(0);
    }
  }

  @Test
  void persistentJournalSurvivesServiceReconstruction() {
    arrival();
    var restored = new TerminalService(new Database(db.url), clock);
    assertFalse(restored.processOnce());
    assertEquals(1, count("business_events"));
  }

  @AfterEach
  void close() {
    db.close();
  }

  @Test
  void routerInternalErrorSuppressesSqlDetails() throws Exception {
    try (var c = db.open()) {
      Database.update(c, "DROP TABLE vehicles CASCADE");
    }
    var r =
        new Router(service, auth, 120)
            .handle(
                "GET",
                "/api/vehicles",
                "Bearer " + env.get("ROLEOS_READER_TOKEN"),
                "",
                "failed-schema");
    assertEquals(500, r.status());
    assertFalse(r.body().contains("SELECT"));
    assertFalse(r.body().contains("SQLException"));
  }

  @Test
  void configurationRequiresDistinctStrongSecrets() {
    var wrong = new HashMap<>(env);
    wrong.remove("ROLEOS_ALPHA_TOKEN");
    assertThrows(IllegalArgumentException.class, () -> new Auth(wrong));
    wrong.put("ROLEOS_ALPHA_TOKEN", env.get("ROLEOS_BETA_TOKEN"));
    assertThrows(IllegalArgumentException.class, () -> new Auth(wrong));
  }

  @Test
  void reportJoinAntiPatternIsDetected() {
    arrival();
    service.accept(event("A1", "ARRIVAL", "ZEE", "ZEE-A01", 0, VIN), actor("ALPHA"), "duplicate");
    long wrong =
        TerminalService.number(
            Database.first(
                db.query(
                    "SELECT COUNT(*) AS n FROM vehicles v JOIN messages m ON m.vin=v.vin JOIN"
                        + " deliveries d ON d.message_id=m.id")),
            "n");
    assertEquals(2, wrong);
    assertEquals(
        1, TerminalService.number(service.report(actor("READER")).getFirst(), "vehicle_count"));
  }

  @Test
  void scopeFilterPrecedesDisplayLimit() throws Exception {
    try (var c = db.open()) {
      for (int i = 0; i < 210; i++)
        Database.update(
            c,
            "INSERT INTO"
                + " messages(id,partner_id,event_key,transport_id,site_id,vin,payload,payload_hash,status,received_at)"
                + " VALUES (?,?,?,?,?,?,?,?,?,?)",
            TerminalService.uuid(),
            "ALPHA",
            "bulk-" + i,
            "bulk-" + i,
            "ZEE",
            VIN,
            "{}",
            "demo-hash",
            "RECEIVED",
            clock.millis() + i);
      Database.update(
          c,
          "INSERT INTO"
              + " messages(id,partner_id,event_key,transport_id,site_id,vin,payload,payload_hash,status,received_at)"
              + " VALUES (?,?,?,?,?,?,?,?,?,?)",
          TerminalService.uuid(),
          "BETA",
          "older-beta",
          "older-beta",
          "KAL",
          VIN,
          "{}",
          "demo-hash",
          "RECEIVED",
          0);
    }
    assertEquals(1, service.scoped("messages", actor("BETA")).size());
  }

  @Test
  void permanentAck4xxDoesNotRetry() throws Exception {
    arrival();
    var server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
    server.createContext(
        "/ack",
        x -> {
          x.sendResponseHeaders(401, -1);
          x.close();
        });
    server.start();
    try {
      var worker =
          new Worker(
              service,
              "http://127.0.0.1:" + server.getAddress().getPort() + "/ack",
              "test-only-secret-24-characters");
      worker.dispatchOnce();
      assertEquals("DEAD_LETTER", db.query("SELECT status FROM outbox").getFirst().get("status"));
      clock.advance(100_000);
      assertFalse(worker.dispatchOnce());
      assertEquals(1, count("business_events"));
    } finally {
      server.stop(0);
    }
  }
}
