# INC-001 — Partnerberichten ontvangen maar niet verwerkt

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV2; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-14 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

ALPHA ZEE-aankomsten zichtbaar als receipt maar ontbreken in operationeel beeld; fysieke deadline door key user te bevestigen.

## Affected systems

API, message journal, worker, portal

## Symptoms

202 receipt, RECEIVED blijft staan; oudste backlog groeit terwijl /health 200 geeft.

## Hypotheses / counterevidence

H1 worker gepauzeerd; H2 tijdelijke dependencyfout; H3 mappingreject. RECEIVED zonder attempts spreekt tegen H2/H3.

## Investigation

Zelfde receipt/site volgen. Metrics worker_paused=true. Geen message.retry/rejected/committed voor receipt. Controls-audit koppelt pause aan labconfig; database bevat input maar geen business_event/outbox.

## Logs

message.received aanwezig; geen message.committed; request.completed 200 voor health. Illustratieve eventnamen, echte logs apart.

## Database checks

failed-messages, reconciliation en SELECT status,attempts FROM messages; status RECEIVED is niet in failed-query, dus ook scoped journal bekijken.

## Root cause in this scenario

In deze scenariohistorie bleef worker_paused aan na training; healthcheck controleerde DB/API maar niet businessvoortgang.

## Workaround

Businessowner bewaakt betroffen taken en zet geen tweede inputstroom op zonder reconciliatie. Queue blijft durable, geen data-update.

## Permanent fix

Admin zet worker_paused=false met audit, monitor oudste leeftijd en commituitkomsten; alert op backlogleeftijd plus duidelijke einde-trainingcheck.

## Validation / evidence boundary

LiveContract test_04 + pausedWorkerProducesHonestBacklogMetric; businesscommit/outbox precies één, backlogstatus gecontroleerd.

## Communication

“Ontvangst werkt; verwerking ZEE wacht. Geen bewezen dataverlies. We herstellen de verwerking en controleren iedere open sleutel. Volgende update 09:30.”

## Lessons learned

Proceshealth is geen ketenhealth. Maak open trainingcontrols zichtbaar bij overdracht.

## Lab reproduction

request ADMIN PATCH /api/admin/controls {"worker_paused":true}; submit event; inspect journal; set false

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
