# Runbook — missing-data

## Symptoms
Physical action exists but record/report absent
## Impact
Locate vehicle/task and safe operationalstate. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Same key,time,site/source; receipt vs commit vs reportdefinition. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: journal; failed; reconcile; occupancyreport. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
received/rejected/retry, processed and reportquery context. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Unprocessed input,wrongscope,statusdefinition, eventorder or join/filter. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Fix first failed boundary; no fabricated record to fixcounts; businessownerconfirmsphysicalstate. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Operations/data/integration; security if scopeexposure. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Keyset reconciliation, freshness/businesshealth and sourceoftruth. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
