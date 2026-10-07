# Runbook — slow-performance

## Symptoms
Slow request/query/backlog without clear error
## Impact
Which task/volume/deadline, not generic servercomplaint. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Baseline/params/rows, timing boundary,locks and inputburst. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: request ADMIN GET /api/admin/diagnostics/slow-query-plan; alerts; record before/after sameworkload. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
Mean request metric is cumulative; do not inventp95; eventtime/queueage. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Expensive query,waiting lock,callback head-of-line,too muchinput. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Bound scope, fix measured cause, reviewed index/scheduler change; no blind tuning. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
DBA/runtime/integration capacityowner as evidence indicates. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Representative loadbaseline, accepted target and alert. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
