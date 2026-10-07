# Post-deployment validation

1. Verify artifact hash/version, actual deployedmarker, schema_version, mappingcontrol and secrets references, not values.
2. Health hits DB; check readiness and unexpected first errors. Verify401/403 and hiddenobject404.
3. Submit unique synthetic initialarrival for each site;202receipt →PROCESSED→vehicle/event/audit/outbox.
4. Repeat unchanged businesskey/new transportID:200duplicate, no second event/vehicle. Change businesspayload:409.
5. Confirm signed ACK callbackreceipt and SENT or explain boundedpendingstatus; no businessreplay.
6. UAT correction correctversion/reason;stale409,reader403,invalidsite400;hold/release requires businessdecision.
7. SQLreconciliation empty; reportcounts currentvehicles, not inputs. Distinguish snapshot/time and route/site.
8. Observe backlog/oldest-age/alerts and app/containerlog in agreed nazorgwindow. Testfaults must return intendedstate.
9. Businessacceptance, support/training handover and remainingrisk record. Close release only with actual evidence and explicit owner.

`smoke` creates only syntheticdata; otherwise health/failed/reconcile are read-only. Acceptancefaulttests mutate only dedicated lab and reset controls. These must never run on an unapproved productiontarget.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
