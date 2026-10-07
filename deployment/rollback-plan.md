# Rollback / recovery plan

Trigger: critical acceptance failure, schema/data inconsistency, wrongscope, unsafe transition or unknown state. Releaseowner freezes further changes, inventories completedsteps and current app/config/schema/mapping/data. Businessowner determines temporary physical workflow. Supervisor/runtime/dataowners decide compatible back-out vs forwardfix vs fresh restore.

App/WAR back-out only when previous code compatible with current schema/data. Controls/mapping rollback audited; history stays. V002 index is additive and can remain. A processed partner event cannot redrive; removing outbox or altering journal to regenerate state is forbidden. Different transport IDs with same key already idempotent.

Offline recovery lab: stop app → DbTool backup into new runtime snapshot → record SHA256 → restore only to **fresh** file database → reopen/reconcile/compare snapshot keys → deploy compatible WAR/controls → business+ACK checks → handle events after snapshot through explicit ledger. Original database never overwritten automatically. Snapshot truncation or schema mismatch is no-go. No claimed zero-data-loss outside checked snapshot/in-flight boundary.

Actual Oracle/enterprise backup, RPO/RTO and restore ownership not simulated as productproof. Those require vendor/DBA procedures and real rehearsal. Workaround may be safe while permanentfix proceeds but has owner/limits/enddate/reconciliation.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
