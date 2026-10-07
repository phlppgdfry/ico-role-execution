# Runbook — database-issue

## Symptoms
SQL error/lockwait, missing records or DB readiness failure
## Impact
Data integrity and all DB-dependent flows. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Schema version, correct target/filelock, recent migration; no direct DML. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: reconcile; request ADMIN GET /api/admin/diagnostics/recent-errors; offline schema query only with owner. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
database.error SQLstate; deployment/schema history. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Wrong schema, locked file, resource issue or incompatible migration. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Use approved recovery path; snapshot/restore fresh target after stopping app; audit data differences. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
DB/runtimeowner; do not kill arbitrary session/process. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Migration gate, actual backup/restore rehearsal, bound queries. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
