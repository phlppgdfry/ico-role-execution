# Runbook — malformed-message

## Symptoms
400 syntax/validation or async UNKNOWN_LOCATION
## Impact
Only affected samples; transport !=businesssuccess. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
Shape/types/date/mandatory/extra; businesscode contract and site. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: Submit edi/samples through partner; failed and journal read. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
MALFORMED_JSON,VALIDATION_ERROR or message.rejected. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
Bad syntax/type/futuretime/unknownfield or code/catalogwrong. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
Sender corrects contract; samekey changedpayload409 must explicit ownerdecision; mapping via CHG003. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
Partnercontractowner/businessmasterdata. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
Strict validation, samples and negative tests. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
