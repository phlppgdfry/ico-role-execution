# Runbook — deployment-failure

## Symptoms
WAR failedmarker,wrong version/schema,postdeploy task failure
## Impact
Hold go-live; avoid mixedversion effects. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Manifest/hash, target config,secrets keys,schema,current marker; stop unplanned changes. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: release-manifest; health; actual server-log; signed window checklist. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
WildFly .failed/server.log, initexception withoutsecret. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Wrong artifact/env,initcredential,DBfilelock or incompatible schema. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Inventory state; safe compatible WAR revert or fresh data recovery/forwardfix; go/no-goowner. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Releaseowner+runtime/data+vendor, supervisor decision. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Preflight/config/UAT and restore rehearsal. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
