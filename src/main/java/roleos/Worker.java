package roleos;

import static roleos.Database.*;

import java.net.URI;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.sql.*;
import java.time.*;
import java.util.*;
import javax.crypto.*;
import javax.crypto.spec.SecretKeySpec;

public final class Worker {
  private final TerminalService service;
  private final URI callback;
  private final String secret;
  private final HttpClient client;

  public Worker(TerminalService service, String callback, String secret) {
    this.service = service;
    this.callback = URI.create(callback);
    this.secret = secret;
    if (secret == null || secret.length() < 24)
      throw new IllegalArgumentException("Set ROLEOS_ACK_SECRET");
    if (!this.callback.getScheme().equals("http")
        || !Set.of("127.0.0.1", "localhost").contains(this.callback.getHost()))
      throw new IllegalArgumentException("Lab callback must be loopback HTTP");
    client =
        HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(1))
            .followRedirects(HttpClient.Redirect.NEVER)
            .build();
  }

  public static String signature(String secret, String payload) {
    try {
      Mac mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
      return HexFormat.of().formatHex(mac.doFinal(payload.getBytes(StandardCharsets.UTF_8)));
    } catch (Exception e) {
      throw new IllegalStateException(e);
    }
  }

  public boolean dispatchOnce() {
    Database db = service.db;
    Map<String, Object> row =
        first(
            db.query(
                "SELECT * FROM outbox WHERE status IN ('PENDING','RETRY_WAIT') AND"
                    + " next_attempt_at<=? ORDER BY created_at,id FETCH FIRST 1 ROW ONLY",
                service.clock.millis()));
    if (row == null) return false;
    String id = (String) row.get("id"),
        correlation = (String) row.get("message_id"),
        payload = (String) row.get("payload");
    int attempt = (int) TerminalService.number(row, "attempts") + 1;
    String error = null;
    try {
      if (db.flag("ack_timeout")) throw new java.io.IOException("Sandbox timeout");
      HttpRequest request =
          HttpRequest.newBuilder(callback)
              .timeout(Duration.ofSeconds(2))
              .header("Content-Type", "application/json")
              .header("X-RoleOS-Signature", signature(secret, payload))
              .POST(HttpRequest.BodyPublishers.ofString(payload))
              .build();
      HttpResponse<Void> response = client.send(request, HttpResponse.BodyHandlers.discarding());
      if (response.statusCode() < 200 || response.statusCode() >= 300)
        error = "ACK_HTTP_" + response.statusCode();
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      return false;
    } catch (java.io.IOException e) {
      error = "ACK_TIMEOUT_OR_UNAVAILABLE";
    }
    try (Connection c = db.open()) {
      if (error == null) {
        update(
            c,
            "UPDATE outbox SET status='SENT',attempts=?,sent_at=?,last_error=NULL WHERE id=?",
            attempt,
            service.clock.millis(),
            id);
        Json.log("ack.sent", correlation, Map.of("attempt", attempt));
      } else {
        boolean terminal = attempt >= 5 || error.startsWith("ACK_HTTP_4");
        update(
            c,
            "UPDATE outbox SET status=?,attempts=?,next_attempt_at=?,last_error=? WHERE id=?",
            terminal ? "DEAD_LETTER" : "RETRY_WAIT",
            attempt,
            service.clock.millis() + TerminalService.backoff(attempt),
            error,
            id);
        Json.log("ack.failed", correlation, Map.of("attempt", attempt, "error_code", error));
      }
    } catch (SQLException e) {
      throw new IllegalStateException("ACK journal failed", e);
    }
    return true;
  }

  public void tick() {
    service.processOnce();
    dispatchOnce();
  }
}
