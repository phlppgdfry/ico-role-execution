# Architecture decision records

## ADR-001 — One modular monolith
Context: role cares about reliable delivery and core/integration understanding, not service count. Decision: Java router/service/worker/JDBC in one deployable WAR. Consequence: low setup cost, cohesive transaction; only one active workerinstance. Alternative Kafka/microservices rejected without scale requirement.

## ADR-002 — H2 instead of Oracle in local execution
Decision: real relational constraints/transactions and Oracle-compatibility mode; explicitly not Oracle implementation. Consequence: operational concepts testable without license/credentials. Oracle port needs datatype/sequence/SQL/locking/plan/backup review, actual JDBC and product UAT. Do not market H2 tests as Oracle test coverage.

## ADR-003 — Durable outbox
Reason: ACK may fail after businesscommit. Decision: queue ACK atomically with effect and retry independently. Consequence: at-least-once ACK; partner receiver deduplicates ack_id. No exactly-once-network-delivery claim.

## ADR-004 — Separate transport and business keys
Retry transport-ID may change. Decision: dedup on partner/event_key plus canonical business hash. Consequence: changed business payload is conflict; transport attempts can repeat visibly without new event.

## ADR-005 — Local-only fault controls and credentials
Testable failure controls require admin, audit, allowlist and loopback. Not production incident tooling. No public demo with mutation keys; no OAuth/SSO implementation claim. Secrets runtime-only.

## ADR-006 — Genuine WAR, fast local adapter
Both adapters reuse Router/TerminalService. Local development can run on JDK with no server install; WildFly lab verifies Servlet mappings/lifecycle separately. Current tested target is EE10 WildFly distribution 41.0.1, not asserted ICO version.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
