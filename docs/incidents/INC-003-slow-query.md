# INC-003 — Langzame diagnosequery / indexpad controleren

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV3; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-16 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Tweede lijn vindt relevante errors te traag bij grotere volumes; timing in verhaal is geen gemeten benchmark.

## Affected systems

Journal query, index, report/diagnostic workload

## Symptoms

Filtering op status/error vraagt onderzoek van plan en rijen; geen fictieve voor/na-latencycijfers.

## Hypotheses / counterevidence

H1 onbegrensde scan; H2 lockwait; H3 volume/parameters; H4 runtimepool. Gebruik plan/locks/timing om te onderscheiden.

## Investigation

Run EXPLAIN via allowlisted slow-query-plan, noteer queryparameters en volume. Existing ready-index helpt queuequery; CHG-002 adds separate errorlookup index for diagnosis, not arbitrary optimizer tuning.

## Logs

request.completed timing context; SQLstate bij timeout; actual EXPLAIN output saved separately when executed.

## Database checks

slow-query-plan; diagnostic failed-messages bounded 200; V002 errorindex idempotent. H2 plan is geen Oracle executionplan.

## Root cause in this scenario

Scenario: errorlookup niet specifiek ondersteund en performance-eis niet gemeten; oorzaak/verbetering moet op representatieve dataset bevestigd worden.

## Workaround

Filter op bekende receipt/site/tijd en gebruik bounded queries; export niet de hele dataset tijdens incident.

## Permanent fix

Reviewed additive index via CHG-002, DBA Oracle-portreview, measurement before and after under same workload.

## Validation / evidence boundary

HTTP test_07 executes actual EXPLAIN; migration/recovery test confirms schema2; no speedup claim without measured baseline.

## Communication

“We begrenzen diagnosequery en beoordelen plan/volume. Er is nog geen bewijs voor algemene platformuitputting. Productie-DBA bepaalt eventuele indexchange.”

## Lessons learned

Index is geen magische fix; keyselectivity/locks/parameter scope eerst.

## Lab reproduction

request ADMIN GET /api/admin/diagnostics/slow-query-plan

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
