# Database operations

H2 2.5.252 / JDBC / MODE=Oracle is the tested lab. It is not Oracle Database and does not prove Oracle optimiser, PL/SQL, RAC, backup or AIX behaviour. Canonical schema: `src/main/resources/schema.sql`; reviewed mirror: `database/schema/001-terminal.sql`. Author script synchronises queries and schema; repository audit compares bytes.

## Tables and invariants

sites/partners/locations are synthetic masterdata. messages is durable business-key journal with UNIQUE(partner_id,event_key), original input and canonical payload hash. deliveries records repeat transport attempts. vehicles carries owner/site/location/state/hold/version and event/processing times. business_events links a message at most once. audit_log records actor, old/new, reason and correlation. outbox is unique per processed message. controls contains explicit lab configuration/faults. schema_version gives migration evidence.

Foreign keys/checks/indexes enforce structure. Worker transaction commits vehicle + event + audit + outbox + processed status together. Timestamp ordering and optimistic version checks avoid silent lost updates. Only one app/worker instance is supported; JVM synchronization is not a cluster lock. Per-request JDBC connection, no enterprise pool. Startup masterdata MERGE does not reset transactional history or controls.

## Diagnostic queries — all read-only

| Query | Purpose | Interpretation |
|---|---|---|
| failed-messages.sql | Open retry/reject/dead-letter | Separate transient error from businessreject; no blanket replay |
| duplicate-records.sql | Business-key duplicates | Empty because unique constraint; delivery duplicates are allowed |
| recent-errors.sql | Last 50 journal errors | Cumulative bounded list, not a time-window failure rate |
| reconciliation.sql | Processed/event/outbox consistency | Empty expected; open ACK status is not missing businesscommit |
| slow-query-plan.sql | Real EXPLAIN plan for queue query | Inspect indexed access; no invented latency improvement |
| outbox-status.sql | Commit/ACK separation | PROCESSED + ACK RETRY_WAIT means only acknowledgement retry |
| occupancy.sql | Current unique vehicles by site/partner/state | Do not count message/delivery rows as vehicles |
| data-quality.sql | Site/location inconsistency | Empty expected; functional rules plus DB constraint boundaries |

Online diagnostics are allowlisted through `/api/admin/diagnostics/{name}`. No arbitrary SQL API. `python3 src/scripts/manage.py failed` and `reconcile` are online. Do not open the file DB from a separate process while the app owns its file lock.

## Offline maintenance

Stop app before file-db migration/backup. DbTool supports a SCRIPT snapshot, fresh-target restore and reviewed migration file inside runtime only. A snapshot is synthetic lab data, not enterprise backup strategy. H2 DDL may auto-commit: schema changes need explicit recovery, not an assumed transaction rollback. Index V002 is additive; rollback can leave a harmless index, whereas data restore requires a fresh destination and explicit validation.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
