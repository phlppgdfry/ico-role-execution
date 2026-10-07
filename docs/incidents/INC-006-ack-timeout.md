# INC-006 — Partner-ACK faalt na geslaagde businesscommit

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV2; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-19 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Partner mist confirmation; intern voertuig correct. Retry business would be risky without dedup.

## Affected systems

Outbox, dispatcher, local callback

## Symptoms

Message PROCESSED, outbox RETRY_WAIT, ACK_TIMEOUT_OR_UNAVAILABLE; partner may send duplicate.

## Hypotheses / counterevidence

H1 callbacktimeout/unavailable; H2 commit missing; H3 HMAC rejected. Outboxstatus/commit distinguish.

## Investigation

Compare journal/business_event/outbox and callbackjournal on ack_id. Loss simulated with ack_timeout; actual HTTP call/HMAC also exercised. Repair acknowledgement only.

## Logs

message.committed before ack.failed; then ack.sent after recovery; same correlation/message ID.

## Database checks

outbox-status + reconciliation; unique business_events/message relation.

## Root cause in this scenario

Scenario: response path/callback unavailable after commit; sender confused receipt and outcome. No businessrollback.

## Workaround

Tell partner commit confirmed; maintain bounded ACK queue; no re-import to generate confirmation.

## Permanent fix

CHG-001 independent ACK retries/outbox, idempotent signed receiver, bounded delays and alert. Restore callback safely.

## Validation / evidence boundary

lostAckDoesNotReplayBusinessMutation plus HTTP/partner receipt; event remains one and ACK SENT.

## Communication

“Uw event is intern verwerkt; bevestiging wacht door callbackstoring. We herstellen uitsluitend de confirmationstroom. De eventkey blijft gelijk bij eventuele retry.”

## Lessons learned

Network exactly-once is not promised; durable outbox plus receiver dedup protects effect.

## Lab reproduction

ack_timeout true; smoke receipt; outbox-status; false; wait retry

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
