# Observability / proactive detection

JSON logs: timestamp UTC, event, correlation_id, method/path/status or message/error/attempt/version/site. Request correlation supplied safe [A-z0-9_-] or UUID; message worker/ACK logs use stable receipt ID. Never log bearer/secret/body. audit_log is separate: actor/action/entity/before/after/reason/time. stdout goes to runtime/app.log or WildFly server.log; lifecycle/runtime errors remain distinguishable.

Metrics are actual database statuses, oldest pending age, open/exhausted ACKs and cumulative request/error count plus mean completed request duration. No fabricated p95, poolconnections or availability. 200-row UI list is not full reconciliation; SQL aggregate/consistency query covers all rows. Thresholds are local training targets, not ICO SLA. Open rejection count is triage inventory, not an interval failure rate; expected labs intentionally trigger it.

Health GET /health reads DB and reports app version/readiness. Forced API fault returns 503; worker pause leaves technical health green, so backlog/last businessoutcome must also be checked. “Green process” is not “healthy chain”. Dashboard schema defines panels; portal shows subset, CLI alerts uses full metrics. Log summary automates grouping but never concludes root cause by error count alone.

Example: oldest pending ≥30s warns worker-oncall; investigate reception/last commit/controls. Dead letter ≥1 raises critical review; businessimpact still determines incidentseverity. Metrics polling 120 actor requests/minute quota shared by role; use appropriate interval, not uncontrolled refreshloop. Production alert suppression/window/escalation and real instrumentation require agreed workload measurements.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
