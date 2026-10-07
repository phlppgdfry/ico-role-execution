# INC-009 — Rapportcijfers wijken af door eventjoin

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV3; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-22 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Weekrapport kan verkeerde operationele indruk geven; bron/definitie afstemmen.

## Affected systems

Reporting SQL, deliveries/events, CSV

## Symptoms

Join count grows with retries/transitions while current vehicle inventory unchanged.

## Hypotheses / counterevidence

H1 one-to-many join; H2 different time/scope; H3 stale snapshot; H4 missing source records.

## Investigation

Same snapshot and businessobject. Compare vehicle keys, grouped report and illustrative bad join. Events/deliveries represent history, not current stock. Explain difference with one vehicle/two deliveries.

## Logs

Report request correlation/params; no fake refreshplatform. Data evidence from actual queries in test.

## Database checks

occupancy.sql versus anti-pattern-delivery-count.sql (never production report); reconciliation keyset.

## Root cause in this scenario

Scenario: event/deliverygrain used for vehiclecount; lack of accepted reportdatacontract.

## Workaround

Withdraw ambiguous report and show correct scoped vehicle count with explicit definition.

## Permanent fix

PRB-003 reporting grain/definition, test cases null/multiple deliveries/two sites, signed businessacceptance simulated.

## Validation / evidence boundary

reportJoinAntiPatternIsDetected + reportCountsVehiclesNotDeliveriesAndHandlesBothSites; CSV same aggregate.

## Communication

“Afwijking betreft teldefinitie, niet aangetoond voertuigverlies. We vergelijken dezelfde scope en leveren gecorrigeerd rapport met sleutelverklaring.”

## Lessons learned

DISTINCT toevoegen zonder begrip kan echte fouten verbergen.

## Lab reproduction

JUnit bad-join test + occupancy CSV endpoint

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
