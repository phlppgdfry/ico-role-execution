# Runbook — authentication-issue

## Symptoms
401 invalid token,403 scope/role,404 invisible detail
## Impact
One account/task vs global outage. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Identity/route/scope/configowner; no secrets in evidence. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: request READER GET /api/vehicles; use correct role, inspect status only. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
request.completed with correlation/status. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Wrong/old token, role mismatch, partner/site or targetwrong. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Credentialowner repairs config; minimum role only; regression denied requests. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Identity/securityowner if suspected leak; supervisor mandate. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Separate roles/owners, startup configvalidation, secure rotation. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
