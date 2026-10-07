package roleos;

import static roleos.Database.*;

import com.fasterxml.jackson.databind.JsonNode;
import java.sql.*;
import java.time.*;
import java.util.*;

/** Single-instance lab service. Synchronization is not a distributed lock. */
public final class TerminalService {
  public final Database db;
  public final Clock clock;

  public TerminalService(Database db, Clock clock) {
    this.db = db;
    this.clock = clock;
  }

  public record Receipt(String id, String status, boolean duplicate) {}

  public static String uuid() {
    return UUID.randomUUID().toString();
  }

  public static long number(Map<String, Object> row, String key) {
    return ((Number) row.get(key)).longValue();
  }

  public static void audit(
      Connection c,
      Auth.Actor actor,
      String action,
      String entity,
      String before,
      String after,
      String reason,
      String correlation,
      long now)
      throws SQLException {
    update(
        c,
        "INSERT INTO audit_log VALUES (?,?,?,?,?,?,?,?,?)",
        uuid(),
        actor.name(),
        action,
        entity,
        before,
        after,
        reason,
        correlation,
        now);
  }

  public synchronized Receipt accept(JsonNode n, Auth.Actor actor, String correlation) {
    actor.require("PARTNER");
    Json.allowed(
        n,
        Set.of(
            "message_id",
            "event_key",
            "partner_id",
            "site_id",
            "vin",
            "event_type",
            "location",
            "event_at",
            "expected_version"));
    var canonical = new LinkedHashMap<String, Object>();
    for (String key :
        List.of("event_key", "partner_id", "site_id", "vin", "event_type", "location"))
      canonical.put(
          key,
          Json.required(
              n,
              key,
              switch (key) {
                case "vin" -> 17;
                case "site_id" -> 8;
                case "partner_id" -> 16;
                case "location" -> 32;
                default -> 64;
              }));
    String transport = Json.required(n, "message_id", 64),
        partner = (String) canonical.get("partner_id"),
        site = (String) canonical.get("site_id"),
        vin = (String) canonical.get("vin");
    if (!actor.partner().equals(partner) || !actor.sites().contains(site))
      throw new ApiError(403, "FORBIDDEN_SCOPE", "Partner/site mismatch");
    if (!vin.matches("[A-Z0-9]{17}"))
      throw new ApiError(
          400,
          "VALIDATION_ERROR",
          "Synthetic vehicle id must be 17 uppercase alphanumeric characters");
    if (!Set.of("ARRIVAL", "MOVE", "DEPARTURE").contains(canonical.get("event_type")))
      throw new ApiError(400, "VALIDATION_ERROR", "Unknown event_type");
    long eventAt;
    try {
      eventAt = Instant.parse(Json.required(n, "event_at", 40)).toEpochMilli();
    } catch (DateTimeException e) {
      throw new ApiError(400, "VALIDATION_ERROR", "event_at must be an ISO-8601 instant");
    }
    if (eventAt > clock.millis() + 300_000)
      throw new ApiError(400, "VALIDATION_ERROR", "event_at exceeds five-minute future tolerance");
    canonical.put("event_at", eventAt);
    canonical.put("expected_version", Json.version(n));
    String hash = Json.hash(Json.write(canonical));
    try (Connection c = db.open()) {
      c.setAutoCommit(false);
      try {
        Map<String, Object> existing =
            first(
                query(
                    c,
                    "SELECT id,status,payload_hash FROM messages WHERE partner_id=? AND"
                        + " event_key=?",
                    partner,
                    canonical.get("event_key")));
        boolean duplicate = existing != null;
        String id = duplicate ? (String) existing.get("id") : uuid();
        if (duplicate && !hash.equals(existing.get("payload_hash")))
          throw new ApiError(
              409, "IDEMPOTENCY_CONFLICT", "Same event_key with different business payload");
        if (!duplicate)
          update(
              c,
              "INSERT INTO"
                  + " messages(id,partner_id,event_key,transport_id,site_id,vin,payload,payload_hash,status,received_at)"
                  + " VALUES (?,?,?,?,?,?,?,?,?,?)",
              id,
              partner,
              canonical.get("event_key"),
              transport,
              site,
              vin,
              Json.write(n),
              hash,
              "RECEIVED",
              clock.millis());
        update(
            c,
            "INSERT INTO deliveries VALUES (?,?,?,?,?)",
            uuid(),
            id,
            transport,
            duplicate,
            clock.millis());
        c.commit();
        Json.log(
            duplicate ? "message.duplicate" : "message.received",
            correlation,
            Map.of("message_id", id, "site", site));
        return new Receipt(id, duplicate ? (String) existing.get("status") : "RECEIVED", duplicate);
      } catch (SQLException | RuntimeException e) {
        c.rollback();
        throw e;
      }
    } catch (SQLException e) {
      throw new IllegalStateException("Acceptance transaction failed", e);
    }
  }

  public synchronized boolean processOnce() {
    if (db.flag("worker_paused")) return false;
    Map<String, Object> msg =
        first(
            db.query(
                "SELECT * FROM messages WHERE status IN ('RECEIVED','RETRY_WAIT') AND"
                    + " next_attempt_at<=? ORDER BY received_at,id FETCH FIRST 1 ROW ONLY",
                clock.millis()));
    if (msg == null) return false;
    String id = (String) msg.get("id");
    int attempt = (int) number(msg, "attempts") + 1;
    if (db.flag("dependency_unavailable")) {
      retry(id, attempt, "DEPENDENCY_UNAVAILABLE");
      return true;
    }
    JsonNode n = Json.read((String) msg.get("payload"));
    String location = n.get("location").asText();
    if (db.control("mapping_version", "1").equals("2"))
      location = location.replace("ZEE-A-", "ZEE-A").replace("KAL-B-", "KAL-B");
    try (Connection c = db.open()) {
      c.setAutoCommit(false);
      try {
        String site = n.get("site_id").asText(),
            vin = n.get("vin").asText(),
            partner = n.get("partner_id").asText(),
            type = n.get("event_type").asText();
        long eventAt = Instant.parse(n.get("event_at").asText()).toEpochMilli();
        Map<String, Object> loc =
            first(query(c, "SELECT * FROM locations WHERE location_id=?", location));
        if (loc == null
            || !site.equals(loc.get("site_id"))
            || !Boolean.TRUE.equals(loc.get("active")))
          throw new ApiError(422, "UNKNOWN_LOCATION", "Invalid site/location");
        Map<String, Object> v =
            first(query(c, "SELECT * FROM vehicles WHERE vin=? FOR UPDATE", vin));
        int newVersion;
        if (v == null) {
          if (!type.equals("ARRIVAL") || Json.version(n) != 0)
            throw new ApiError(422, "VEHICLE_NOT_FOUND", "Arrival required before transition");
          newVersion = 1;
          update(
              c,
              "INSERT INTO vehicles VALUES (?,?,?,?,?,?,?,?,?)",
              vin,
              partner,
              site,
              location,
              "ACTIVE",
              false,
              newVersion,
              eventAt,
              clock.millis());
        } else {
          if (!partner.equals(v.get("partner_id")) || !site.equals(v.get("site_id")))
            throw new ApiError(422, "OWNERSHIP_CONFLICT", "Vehicle does not belong to event scope");
          if (Json.version(n) != number(v, "version"))
            throw new ApiError(422, "VERSION_CONFLICT", "Stale expected_version");
          if (eventAt <= number(v, "last_event_at"))
            throw new ApiError(422, "OUT_OF_ORDER", "Event timestamp must increase");
          if (type.equals("ARRIVAL") && !v.get("state").equals("DEPARTED"))
            throw new ApiError(422, "ALREADY_ACTIVE", "Vehicle already active");
          if (!type.equals("ARRIVAL") && !v.get("state").equals("ACTIVE"))
            throw new ApiError(422, "INVALID_TRANSITION", "Vehicle is not active");
          if (type.equals("DEPARTURE") && Boolean.TRUE.equals(v.get("hold_flag")))
            throw new ApiError(422, "HOLD_ACTIVE", "Business hold prevents departure");
          if (type.equals("DEPARTURE") && !location.equals(v.get("location_id")))
            throw new ApiError(
                422, "LOCATION_CONFLICT", "Departure location differs from current location");
          newVersion = (int) number(v, "version") + 1;
          update(
              c,
              "UPDATE vehicles SET location_id=?,state=?,version=?,last_event_at=?,updated_at=?"
                  + " WHERE vin=?",
              location,
              type.equals("DEPARTURE") ? "DEPARTED" : "ACTIVE",
              newVersion,
              eventAt,
              clock.millis(),
              vin);
        }
        update(
            c,
            "INSERT INTO business_events VALUES (?,?,?,?,?,?)",
            uuid(),
            id,
            vin,
            type,
            eventAt,
            clock.millis());
        var worker = new Auth.Actor("integration-worker", "SYSTEM", partner, Set.of(site));
        audit(
            c,
            worker,
            type,
            vin,
            v == null ? null : (String) v.get("location_id"),
            location,
            "Partner event " + n.get("event_key").asText(),
            id,
            clock.millis());
        var ack =
            Map.of(
                "ack_id",
                id,
                "event_key",
                n.get("event_key").asText(),
                "partner_id",
                partner,
                "site_id",
                site,
                "status",
                "PROCESSED",
                "business_version",
                newVersion);
        update(
            c,
            "INSERT INTO outbox(id,message_id,payload,status,created_at) VALUES (?,?,?,?,?)",
            uuid(),
            id,
            Json.write(ack),
            "PENDING",
            clock.millis());
        update(
            c,
            "UPDATE messages SET status='PROCESSED',attempts=?,processed_at=?,last_error=NULL WHERE"
                + " id=?",
            attempt,
            clock.millis(),
            id);
        c.commit();
        Json.log("message.committed", id, Map.of("version", newVersion, "site", site));
      } catch (SQLException | RuntimeException e) {
        c.rollback();
        throw e;
      }
    } catch (ApiError e) {
      mark(id, "REJECTED", attempt, e.code, 0);
      Json.log("message.rejected", id, Map.of("error_code", e.code));
    } catch (SQLException e) {
      retry(id, attempt, "DATABASE_ERROR");
      Json.log("database.error", id, Map.of("sql_state", String.valueOf(e.getSQLState())));
    }
    return true;
  }

  private void retry(String id, int attempt, String error) {
    mark(
        id,
        attempt >= 5 ? "DEAD_LETTER" : "RETRY_WAIT",
        attempt,
        error,
        clock.millis() + backoff(attempt));
    Json.log("message.retry", id, Map.of("attempt", attempt, "error_code", error));
  }

  public static long backoff(int attempt) {
    return Math.min(16_000, 1000L << (Math.min(5, Math.max(1, attempt)) - 1));
  }

  private void mark(String id, String status, int attempt, String error, long next) {
    try (Connection c = db.open()) {
      update(
          c,
          "UPDATE messages SET status=?,attempts=?,last_error=?,next_attempt_at=? WHERE id=?",
          status,
          attempt,
          error,
          next,
          id);
    } catch (SQLException e) {
      throw new IllegalStateException("Could not journal failure", e);
    }
  }

  public synchronized void redrive(String id, Auth.Actor actor, String reason, String correlation) {
    actor.require("ADMIN");
    if (reason.isBlank() || reason.length() > 240)
      throw new ApiError(400, "VALIDATION_ERROR", "reason required, maximum 240 characters");
    try (Connection c = db.open()) {
      c.setAutoCommit(false);
      try {
        Map<String, Object> m = first(query(c, "SELECT * FROM messages WHERE id=? FOR UPDATE", id));
        if (m == null) throw new ApiError(404, "NOT_FOUND", "Message absent");
        if (!Set.of("REJECTED", "DEAD_LETTER", "RETRY_WAIT").contains(m.get("status")))
          throw new ApiError(
              409, "REDRIVE_FORBIDDEN", "Processed or active message cannot be re-driven");
        update(
            c,
            "UPDATE messages SET status='RECEIVED',attempts=0,last_error=NULL,next_attempt_at=0"
                + " WHERE id=?",
            id);
        audit(
            c,
            actor,
            "REDRIVE",
            id,
            (String) m.get("status"),
            "RECEIVED",
            reason,
            correlation,
            clock.millis());
        c.commit();
      } catch (SQLException | RuntimeException e) {
        c.rollback();
        throw e;
      }
    } catch (SQLException e) {
      throw new IllegalStateException(e);
    }
  }

  public synchronized Map<String, Object> correct(
      String vin, JsonNode n, Auth.Actor actor, String correlation, boolean hold) {
    actor.require("OPERATOR", "ADMIN");
    Json.allowed(
        n,
        hold
            ? Set.of("expected_version", "hold", "reason", "decision_ref")
            : Set.of("expected_version", "location", "reason"));
    String reason = Json.required(n, "reason", 200);
    int expected = Json.version(n);
    if (hold && n.has("decision_ref")) Json.required(n, "decision_ref", 32);
    try (Connection c = db.open()) {
      c.setAutoCommit(false);
      try {
        Map<String, Object> v =
            first(query(c, "SELECT * FROM vehicles WHERE vin=? FOR UPDATE", vin));
        if (v == null || !actor.canSee(v))
          throw new ApiError(404, "NOT_FOUND", "Vehicle absent in scope");
        if (!v.get("state").equals("ACTIVE"))
          throw new ApiError(409, "INVALID_TRANSITION", "Vehicle not active");
        if (expected != number(v, "version"))
          throw new ApiError(409, "VERSION_CONFLICT", "Reload current vehicle");
        String before, after, action;
        if (hold) {
          JsonNode flag = n.get("hold");
          if (flag == null || !flag.isBoolean())
            throw new ApiError(400, "VALIDATION_ERROR", "hold must be boolean");
          if (!flag.asBoolean()) {
            actor.require("ADMIN");
            Json.required(n, "decision_ref", 32);
          }
          before = String.valueOf(v.get("hold_flag"));
          after =
              flag.asText()
                  + (flag.asBoolean() ? "" : "; decision_ref=" + n.get("decision_ref").asText());
          action = "HOLD_CHANGE";
          update(
              c,
              "UPDATE vehicles SET hold_flag=?,version=version+1,updated_at=? WHERE vin=?",
              flag.asBoolean(),
              clock.millis(),
              vin);
        } else {
          String location = Json.required(n, "location", 32);
          Map<String, Object> l =
              first(
                  query(
                      c,
                      "SELECT * FROM locations WHERE location_id=? AND site_id=? AND active=TRUE",
                      location,
                      v.get("site_id")));
          if (l == null) throw new ApiError(400, "UNKNOWN_LOCATION", "Location not valid for site");
          before = (String) v.get("location_id");
          after = location;
          action = "LOCATION_CORRECTION";
          update(
              c,
              "UPDATE vehicles SET location_id=?,version=version+1,updated_at=? WHERE vin=?",
              location,
              clock.millis(),
              vin);
        }
        audit(c, actor, action, vin, before, after, reason, correlation, clock.millis());
        c.commit();
        return first(query(c, "SELECT * FROM vehicles WHERE vin=?", vin));
      } catch (SQLException | RuntimeException e) {
        c.rollback();
        throw e;
      }
    } catch (SQLException e) {
      throw new IllegalStateException(e);
    }
  }

  public synchronized void controls(JsonNode n, Auth.Actor actor, String correlation) {
    actor.require("ADMIN");
    Set<String> flags =
        Set.of("worker_paused", "dependency_unavailable", "ack_timeout", "force_api_failure");
    Set<String> all = new HashSet<>(flags);
    all.add("mapping_version");
    Json.allowed(n, all);
    try (Connection c = db.open()) {
      c.setAutoCommit(false);
      try {
        for (var entry : n.properties()) {
          String key = entry.getKey(), value = entry.getValue().asText();
          if (flags.contains(key) && !entry.getValue().isBoolean())
            throw new ApiError(400, "VALIDATION_ERROR", "Control must be boolean");
          if (key.equals("mapping_version")
              && (!entry.getValue().isTextual() || !Set.of("1", "2").contains(value)))
            throw new ApiError(400, "VALIDATION_ERROR", "mapping_version must be 1 or 2");
          String before = db.control(key, key.equals("mapping_version") ? "1" : "false");
          update(c, "MERGE INTO controls KEY(control_name) VALUES (?,?)", key, value);
          audit(
              c,
              actor,
              "LAB_CONTROL",
              key,
              before,
              value,
              "Explicit sandbox control",
              correlation,
              clock.millis());
        }
        c.commit();
      } catch (SQLException | RuntimeException e) {
        c.rollback();
        throw e;
      }
    } catch (SQLException e) {
      throw new IllegalStateException(e);
    }
  }

  public List<Map<String, Object>> scoped(String table, Auth.Actor actor) {
    String select =
        switch (table) {
          case "messages" ->
              "SELECT"
                  + " id,partner_id,event_key,site_id,vin,status,attempts,received_at,processed_at,last_error"
                  + " FROM messages";
          case "vehicles" -> "SELECT * FROM vehicles";
          default -> throw new IllegalArgumentException("Table not permitted");
        };
    var params = new ArrayList<Object>(actor.sites());
    String sql =
        select
            + " WHERE site_id IN ("
            + String.join(",", Collections.nCopies(params.size(), "?"))
            + ")";
    if (actor.partner() != null) {
      sql += " AND partner_id=?";
      params.add(actor.partner());
    }
    sql += table.equals("messages") ? " ORDER BY received_at DESC,id" : " ORDER BY vin";
    return db.query(sql + " FETCH FIRST 200 ROWS ONLY", params.toArray());
  }

  public Map<String, Object> metrics() {
    var result = new LinkedHashMap<String, Object>();
    for (String status : List.of("RECEIVED", "RETRY_WAIT", "PROCESSED", "REJECTED", "DEAD_LETTER"))
      result.put(
          "messages_" + status.toLowerCase(),
          number(
              first(db.query("SELECT COUNT(*) AS n FROM messages WHERE status=?", status)), "n"));
    var oldest =
        first(
            db.query(
                "SELECT MIN(received_at) AS oldest FROM messages WHERE status IN"
                    + " ('RECEIVED','RETRY_WAIT')"));
    result.put(
        "oldest_pending_seconds",
        oldest.get("oldest") == null
            ? 0
            : Math.max(0, (clock.millis() - number(oldest, "oldest")) / 1000));
    result.put(
        "ack_pending",
        number(
            first(
                db.query(
                    "SELECT COUNT(*) AS n FROM outbox WHERE status IN ('PENDING','RETRY_WAIT')")),
            "n"));
    result.put(
        "ack_dead_letter",
        number(
            first(db.query("SELECT COUNT(*) AS n FROM outbox WHERE status='DEAD_LETTER'")), "n"));
    result.put("worker_paused", db.flag("worker_paused"));
    return result;
  }

  public List<Map<String, Object>> report(Auth.Actor actor) {
    return db
        .query(
            "SELECT site_id,partner_id,state,COUNT(*) AS vehicle_count,SUM(CASE WHEN hold_flag THEN"
                + " 1 ELSE 0 END) AS held_count FROM vehicles GROUP BY site_id,partner_id,state"
                + " ORDER BY site_id,partner_id,state")
        .stream()
        .filter(actor::canSee)
        .toList();
  }
}
