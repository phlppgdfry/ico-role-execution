package roleos;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.sql.*;
import java.util.*;

public final class Database implements AutoCloseable {
  public final String url;

  public Database(String url) {
    if (!url.startsWith("jdbc:h2:")) throw new IllegalArgumentException("Lab requires H2 URL");
    this.url = url;
    try (Connection c = open()) {
      String schema =
          new String(
              Objects.requireNonNull(getClass().getResourceAsStream("/schema.sql")).readAllBytes(),
              StandardCharsets.UTF_8);
      try (Statement s = c.createStatement()) {
        for (String sql : schema.split(";")) {
          if (!sql.isBlank()) s.execute(sql);
        }
      }
      update(
          c,
          "UPDATE schema_version SET applied_at=? WHERE version=1 AND applied_at=0",
          System.currentTimeMillis());
    } catch (Exception e) {
      throw new IllegalStateException("Database initialization failed", e);
    }
  }

  public Connection open() throws SQLException {
    Connection c = DriverManager.getConnection(url, "sa", "");
    try (Statement s = c.createStatement()) {
      s.execute("SET LOCK_TIMEOUT 3000");
    }
    return c;
  }

  public static int update(Connection c, String sql, Object... params) throws SQLException {
    try (PreparedStatement p = c.prepareStatement(sql)) {
      bind(p, params);
      return p.executeUpdate();
    }
  }

  public static List<Map<String, Object>> query(Connection c, String sql, Object... params)
      throws SQLException {
    try (PreparedStatement p = c.prepareStatement(sql)) {
      p.setQueryTimeout(5);
      bind(p, params);
      try (ResultSet r = p.executeQuery()) {
        var rows = new ArrayList<Map<String, Object>>();
        var meta = r.getMetaData();
        while (r.next()) {
          var row = new LinkedHashMap<String, Object>();
          for (int i = 1; i <= meta.getColumnCount(); i++) {
            Object value = r.getObject(i);
            if (value instanceof Clob clob) value = clob.getSubString(1, (int) clob.length());
            row.put(meta.getColumnLabel(i).toLowerCase(Locale.ROOT), value);
          }
          rows.add(row);
        }
        return rows;
      }
    }
  }

  private static void bind(PreparedStatement p, Object[] params) throws SQLException {
    for (int i = 0; i < params.length; i++) p.setObject(i + 1, params[i]);
  }

  public List<Map<String, Object>> query(String sql, Object... params) {
    try (Connection c = open()) {
      return query(c, sql, params);
    } catch (SQLException e) {
      throw new IllegalStateException("Query failed", e);
    }
  }

  public static Map<String, Object> first(List<Map<String, Object>> rows) {
    return rows.isEmpty() ? null : rows.getFirst();
  }

  public String control(String key, String fallback) {
    Map<String, Object> row =
        first(query("SELECT control_value FROM controls WHERE control_name=?", key));
    return row == null ? fallback : (String) row.get("control_value");
  }

  public boolean flag(String key) {
    return Boolean.parseBoolean(control(key, "false"));
  }

  public void close() {
    try (Connection c = open();
        Statement s = c.createStatement()) {
      s.execute("SHUTDOWN");
    } catch (SQLException e) {
      throw new IllegalStateException("Database shutdown failed", e);
    }
  }

  public List<Map<String, Object>> diagnostic(String name) {
    if (!Set.of(
            "failed-messages",
            "duplicate-records",
            "recent-errors",
            "reconciliation",
            "slow-query-plan",
            "outbox-status")
        .contains(name)) throw new ApiError(404, "NOT_FOUND", "Unknown registered diagnostic");
    try {
      String sql =
          new String(
              Objects.requireNonNull(
                      getClass().getResourceAsStream("/diagnostics/" + name + ".sql"))
                  .readAllBytes(),
              StandardCharsets.UTF_8);
      return query(sql);
    } catch (IOException e) {
      throw new IllegalStateException("Diagnostic unavailable", e);
    }
  }
}
