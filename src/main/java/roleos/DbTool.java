package roleos;

import java.nio.file.*;
import java.sql.*;
import java.util.*;

/** Offline lab-only maintenance. Restore always targets a fresh database. */
public final class DbTool {
  private DbTool() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || !Set.of("backup", "restore", "migrate").contains(args[0]))
      throw new IllegalArgumentException("DbTool backup|restore|migrate path");
    Path path = Path.of(args[1]).toAbsolutePath().normalize();
    if (!path.startsWith(Path.of("runtime").toAbsolutePath().normalize()))
      throw new IllegalArgumentException("Maintenance paths must be inside runtime");
    String url = System.getenv("ROLEOS_DB_URL");
    if (url == null) throw new IllegalArgumentException("Set ROLEOS_DB_URL");
    if (args[0].equals("restore")) {
      String file = url.replaceFirst("^jdbc:h2:file:", "").split(";")[0];
      if (!url.startsWith("jdbc:h2:file:") || Files.exists(Path.of(file + ".mv.db")))
        throw new IllegalArgumentException("Restore requires a fresh file DB destination");
    }
    if (args[0].equals("backup") && Files.exists(path))
      throw new IllegalArgumentException("Refusing to overwrite snapshot");
    if (args[0].equals("backup")) Files.createDirectories(path.getParent());
    try (Connection c = DriverManager.getConnection(url, "sa", "");
        Statement s = c.createStatement()) {
      switch (args[0]) {
        case "backup" -> s.execute("SCRIPT TO '" + path.toString().replace("'", "''") + "'");
        case "restore" -> s.execute("RUNSCRIPT FROM '" + path.toString().replace("'", "''") + "'");
        case "migrate" -> {
          String sql = Files.readString(path);
          c.setAutoCommit(false);
          try {
            for (String statement : sql.split(";")) if (!statement.isBlank()) s.execute(statement);
            Database.update(
                c,
                "UPDATE schema_version SET applied_at=? WHERE applied_at=0",
                System.currentTimeMillis());
            c.commit();
          } catch (SQLException e) {
            c.rollback();
            throw e;
          }
        }
        default -> throw new IllegalArgumentException();
      }
      s.execute("SHUTDOWN");
    }
    System.out.println(
        Json.write(
            Map.of(
                "maintenance",
                args[0],
                "path",
                Path.of("runtime").toAbsolutePath().relativize(path).toString(),
                "simulation",
                true)));
  }
}
