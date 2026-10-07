# Runbook — application-unavailable

## Symptoms
Connection refused,health503,portal task fail
## Impact
Scope site/critical task; preserve physicaltraceability. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Process/container first vs API readiness; latest deployment and controls. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: health; smoke after recovery; inspect owned app/container log. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
application.started / servletdeployment markers / request503. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Appdown, config/DB-initfailure, force_api_failure or network. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Authorized service/config restore; health plus real businesscheck; no blanket restarts. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Runtimeowner for process/OS, officer for chain, operations for workaround. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Rehearsed deployment/availability checks; not health alone. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
