# INC-007 — Dubbele verzending wordt voor dubbele voertuigen aangezien

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV3; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-20 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Business telt dubbele input; data-integriteit moet bewezen worden voordat correctie plaatsvindt.

## Affected systems

API/journal/deliveries/report

## Symptoms

Two transport receipts but one business event; repetition may use new message_id.

## Hypotheses / counterevidence

H1 same key same payload (safe); H2 changed payload same key (409); H3 new key actual event; H4 wrong report join.

## Investigation

Compare partner/event_key, canonicalhash and deliveryjournal, count business_events and current vehicles rather than transport attempts. Concurrent test sends16 requests and creates one effect.

## Logs

message.duplicate distinct request correlations, same system message ID.

## Database checks

duplicate-records empty; count deliveries/message and events separately; occupancy.sql counts vehicles.

## Root cause in this scenario

Scenario: transportattempts interpreted as businessobjects; duplicate prevention works, reporting definition was wrong.

## Workaround

Do not delete records; publish correct definition and reconcile by businesskey.

## Permanent fix

PRB-003 / BR07 / regression report. UNIQUE partner/eventkey plus changed-payload conflict already implemented.

## Validation / evidence boundary

concurrentDuplicateRequestsRemainUnique, reportCountsVehiclesNotDeliveriesAndHandlesBothSites, reportJoinAntiPatternIsDetected.

## Communication

“Er zijn twee afleverpogingen van hetzelfde event, één verwerking en één voertuig. We tonen sleutelbewijs; we verwijderen geen audit-/deliveryrecords om een telling te laten passen.”

## Lessons learned

Dedupbusiness and operationalreport meanings must both be explicit.

## Lab reproduction

Send arrival/duplicate fixtures; inspect deliveries vs occupancy

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
