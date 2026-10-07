# Vendor work package — WP3 integration delivery

Objective: preserve one business effect per eventkey and give accurate aftercommitACK. Deliver: contractprofile/samples, mapping1/2, error semantics, duplicate/concurrency/timeout tests, component/configversion, rollout/recovery instructions and supporthandover. In/outscope explicit; productlicense and actual vendor unknown.

Acceptance evidence: deterministic tests; sample badcode/recovery; transportidchange and payloadconflict; callbackresponse loss; HMAC invalid rejection; bothsites; firstfailurelog/correlation and safetyholds. Provider claiming “works here” without matching sample/version does not close issue. Officer independently validates chain/businessoutcome.

Actionlog (fictief): V-01 aliases verify / partnerowner / 2026-09-24; V-02 signedACKretry demo / integrationvendor / 09-25; V-03 recoverymanifest / runtimeowner / 09-26; V-04 UATtraining / keyuser+officer / 09-27. Escalate missed acceptance or10% forecastdrift with options: reduce scope, move window or add agreedcapacity. Contract/budgetapproval stays assignedowner.

Question to supplier: “For receipt X/eventkey Y at Z UTC, our journal proves commit; outbox shows callbacktimeout. Please provide matching receiverlog/ACK semantics and next testwindow. No credential in reply.” Outsourcing includes documentation/exitknowledge, not surrendering architectureownership.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
