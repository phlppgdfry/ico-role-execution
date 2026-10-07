# Runbook — duplicated-data

## Symptoms
More delivery/event rows than expected objects
## Impact
Determine duplicateeffect vs harmless repeateddelivery. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Business key/hash,transport IDs,vehicle/event/outbox counts. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: duplicate-records; reconciliation; occupancyquery; anti-pattern only in test. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
message.duplicate same receipt; conflict changedpayload. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Expected retries,changedkeys,reportgrainwrong or genuine race. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Unique/atomic enforcement; do not deleteaudit/delivery; correct proved dataissue by authorized plan. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Data/integrationowner; businessdefinitionowner for report. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Concurrent/timeout tests,contractkey agreement and reportnegativefixtures. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
