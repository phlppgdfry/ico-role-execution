# Non-functional requirements — lab targets

| ID | Requirement | Verification / boundary |
|---|---|---|
| NFR01 | No embedded production credential; five distinct ≥24-char bearer secrets | Config refusal, generated .env 0600, secret pattern audit |
| NFR02 | DB commit atomic and repeat transport harmless | JUnit atomicity/concurrent duplicate + HTTP duplicate |
| NFR03 | Bounded request/DB/callback resources | 16 KiB body, 120 actor requests/minute, 5s query, 1s connect/2s ACK |
| NFR04 | Scoped access before list limit | SQL site/partner filter before 200-row display limit; detail 404 outside scope |
| NFR05 | Durable failure/retry state | File journal and restart test; no in-memory-only message queue |
| NFR06 | Evidence without token/rawpayload logs | JSON event/correlation/error/status, audit for mutations |
| NFR07 | Traceable releases and safe recovery | Actual WAR hash, checks, new-target snapshot restore |
| NFR08 | Synthetic-data-only / loopback | Default local ports, callback and CLI allowlist; no TLS claim |
| NFR09 | Operational detection | Open failures, oldest age, queue and ACK alerts; measured metrics only |
| NFR10 | Reproducibility | Java 21/Maven/Python commands and GitHub CI; actual WildFly lab test recorded |

Lab has no guaranteed availability/SLA, no HA, no enterprise pool, no production-scale performance benchmark. List views are bounded at 200, diagnostic/error views at 200 or 50; aggregate reports/reconciliation query all applicable records. API rate-limit is fixed-minute actor quota, no distributed limiter. These boundaries are requirements, not hidden omissions.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
