# Communication pack — concise, actionable samples

## Incident update to business
“ALPHA ZEE-berichten worden ontvangen maar wachten in verwerking. Andere gecontroleerde flows werken. Geen bewezen verlies; we bewaren input en onderzoeken workerstatus. Herstelactie volgt ownerapproval, daarna sleutelcontrole. Volgende update09:30UTC; ETA nog onbekend.”

## Technical explanation to management
“Businesscommit en partnerbevestiging zijn gescheiden. Een callbacktimeout vraagt ACKretry, geen tweede vehiclemutatie. Durableoutbox en idempotency beperken risico. We kiezen deze samenhangende monolith omdat enterpriseproductdetails onbekend zijn; productport vereist aparte validation.”

## External vendor question
“Please correlate receipt X,eventkeyY,10:04UTC against contract/mappingversion2. Our commit is present; callbackdelivery not confirmed. Send redacted receiverstatus and firsterror; no token/payloadcustomerdata. Can we test one sample at11:00?”

## Release announcement
“Lab1.4.0 contains scopedreceipts,controlledcorrections,mappingaliases and aftercommitACK. Testwindow16:00–17:00UTC; simulatedgo/no-go gates apply. Users must keep reason/currentversion; transportreceipt is not businesssuccess. Knownproductboundaries and supportcontact in releaseguide.”

## Change approval request
“CHG003 fixes approvedcodealiases for two sites. Risks: wrongsite/coercion/unsafe replay. Bothsite-negative tests and one-effectredrive gate required. Rollback mapping leaves processedhistory intact. Request explicit supervisor/businessdecision before window.”

## Post-incident summary
“Cause in scenario: trainingpause left active. Dataaccepted,notlost. Recovery cleared control,verifiedvehicle/outbox and oldestage. Prevention: end-trainingcheck and backlogalert with owner. Rootcauseevidence and remainingactions documented; no blame, no falseavailabilitymetric.”

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
