# Runbook — integration-failure

## Symptoms
RETRY_WAIT/DEAD_LETTER, partner missing result
## Impact
Partner/site flow and backlog urgency. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Receipt status, last good step, contract/mapping and callbackjournal. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: failed; request ADMIN GET /api/admin/diagnostics/outbox-status; reconcile. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
received → retry/rejected/committed → ack.failed/sent. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Unavailable dependency, unknowncode, version/order/hold or ACKfailure. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Repair cause, wait bounded retry; admin reasoned redrive only uncommitted failure; ACK only if businesscommitted. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Integrationpartner plus businessowner for semantics. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Idempotence, contractfixtures, oldest-age/deadletter alerts. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
