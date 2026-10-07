# Runbook — api-failure

## Symptoms
401/403/409/429/5xx or transport failure
## Impact
Failed user/partner task, determine site/partner and physical deadline. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
health and actual route/status/correlation; compare one known-good request. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: health; request ADMIN GET /api/messages; log-summary. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
request.completed, request.internal_error; never tokens. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Bad auth/scope, wrong contract, quota, controlled dependency failure or DB exception. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Fix first proved boundary with owner; same eventkey retries only for transient transport/5xx; do not bypass auth. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Service Desk → officer → runtime/data/integration owner; security if exposure. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Contract negative tests, rate/timeout agreement and business-smoke. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
