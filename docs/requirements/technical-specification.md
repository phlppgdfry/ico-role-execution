# Technical specification

Router handles method/path/auth/body/rate/correlation and maps ApiError to public error codes. TerminalService owns validation, scoped reads, transaction transitions, correction and authorized redrive. Business processor and ACK dispatcher independently attempt one eligible item every 200ms; slow ACK does not block processing. Database owns prepared statements, bounded queries and schema. LocalServer and TerminalServlet are adapters for the same implementation; SecurityHeaders protects WAR responses. No Spring/JPA requirement invented.

Canonical businesshash covers eventkey, partner, site, vin, type, mapped input location string, normalized instant and version; transport message_id excluded. Unique DB key prevents semantic duplicate; JVM service synchronization handles concurrent requests in the supported single instance. Original payload kept for diagnosis. Changed eventkey is not automatically the same event: partner must follow contract.

Worker uses current location mapping version, verifies active location/site and current vehicle version under transaction row lock, then vehicle/event/audit/outbox/status commit. Business error rolls back before journalling reject. Transient dependency fault yields bounded retry 1/2/4/8/16 seconds, at most five processing attempts. No production jitter strategy claimed; additional production burst/load control belongs in capacitydesign.

HTTP ACK dispatcher has 1s connect/2s overall timeout, no redirects, loopback target allowlist and HMAC SHA256. 2xx accepted; 4xx permanent, other errors bounded. Outbox plus idempotent callback tolerate response loss. Callback is actual local Python HTTP server, not a fictional external success. Database/script failure cannot produce a false healthy business outcome.

Controls, schema, mapping and artefact versions are distinct release dimensions. Database.schema init does not migrate away user data; additive V002 is separately reviewed/executed offline. File DB locked by one process. Shutdown closes worker then DB, including WAR undeploy. Production extensions require real Oracle JDBC/pool, identity/TLS, distributed worker claim and platformprocedures; see substitutions.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
