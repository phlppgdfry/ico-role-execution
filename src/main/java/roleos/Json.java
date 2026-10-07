package roleos;

import com.fasterxml.jackson.databind.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

public final class Json {
  public static final ObjectMapper MAPPER =
      new ObjectMapper().enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS);

  private Json() {}

  public static String write(Object value) {
    try {
      return MAPPER.writeValueAsString(value);
    } catch (Exception e) {
      throw new IllegalStateException("Cannot serialize", e);
    }
  }

  public static JsonNode read(String value) {
    try {
      return MAPPER.readTree(value);
    } catch (Exception e) {
      throw new ApiError(400, "MALFORMED_JSON", "Expected one JSON object");
    }
  }

  public static String hash(String value) {
    try {
      return HexFormat.of()
          .formatHex(
              MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));
    } catch (NoSuchAlgorithmException e) {
      throw new IllegalStateException(e);
    }
  }

  public static void log(String event, String correlation, Map<String, ?> fields) {
    var values = new LinkedHashMap<String, Object>();
    values.put("timestamp", java.time.Instant.now().toString());
    values.put("event", event);
    values.put("correlation_id", correlation);
    values.putAll(fields);
    System.out.println(write(values));
  }

  public static String required(JsonNode node, String key, int max) {
    JsonNode v = node.get(key);
    if (v == null || !v.isTextual() || v.asText().isBlank() || v.asText().length() > max)
      throw new ApiError(400, "VALIDATION_ERROR", "Invalid field: " + key);
    return v.asText();
  }

  public static int version(JsonNode node) {
    JsonNode v = node.get("expected_version");
    if (v == null || !v.isIntegralNumber() || !v.canConvertToInt() || v.asInt() < 0)
      throw new ApiError(400, "VALIDATION_ERROR", "expected_version must be a nonnegative integer");
    return v.asInt();
  }

  public static void allowed(JsonNode node, Set<String> fields) {
    if (node == null || !node.isObject())
      throw new ApiError(400, "VALIDATION_ERROR", "Expected object");
    node.fieldNames()
        .forEachRemaining(
            k -> {
              if (!fields.contains(k))
                throw new ApiError(400, "VALIDATION_ERROR", "Unknown field: " + k);
            });
  }
}
