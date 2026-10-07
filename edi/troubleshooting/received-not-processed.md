# EDI received but not processed

## Symptoms / impact
202 receipt exists; operational status absent. A receipt proves durable acceptance, not commit. Ask event key, partner/site, expected task and physical deadline.

## First checks
Look up receipt ID using partner token or scoped journal. RECEIVED: worker/backlog; RETRY_WAIT: transient dependency with attempt/next time; REJECTED: contract/business error; DEAD_LETTER: retries exhausted; PROCESSED: inspect outbox/report/display rather than replay business.

## Commands / queries
`python3 src/scripts/manage.py failed`; `request ADMIN GET /api/admin/diagnostics/outbox-status`; `reconcile`. SQL references: failed-messages, recent-errors, reconciliation. These commands are read-only. Do not directly UPDATE status.

## Logs / causes
message.received → message.rejected/retry/committed → ack.failed/sent, joined by system message ID. Common labs: worker_paused, dependency_unavailable, UNKNOWN_LOCATION, VERSION_CONFLICT, OUT_OF_ORDER, HOLD_ACTIVE. TransportID may change across duplicate deliveries.

## Resolution / escalation
For temporary failure remove the cause within mandaat and wait for bounded retry. For permanent reject fix contract/masterdata/mapping through CHG-003, then admin redrive with reason only if no businesscommit. PROCESSED cannot redrive. ACK failure retries only outbox; callback is idempotent. Escalate safety/data/security ambiguity to business/IT owner before correction.

## Prevention
Contract samples, negative tests, oldest-age alert, commit/ACK separation, unique keys and training. Validate actual vehicle outcome, business_events/outbox reconciliation and partner receipt before closing.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
