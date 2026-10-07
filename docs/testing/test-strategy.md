# Test strategy

Unit/domain/database:25 JUnit tests cover validation,strictJSON,date/type/extra/shape,canonicalbusinesskey,concurrentduplicates,hashconflict,partner/sitescope,atomicstate/event/audit/outbox,location/version/order/hold,rolecorrection,transientretry/exhaustion,ACKloss/HMAC/4xx,reportgrain and scopebeforelimit. Fresh in-memoryH2 pertest,closedaftertest; no productioncommand.

Integration/API:7Pythonacceptance tests against an actualrunninglocalserver and the sameWARonWildFly. Bothsites/signedACK;401/403/404/409;mappingredrive;pause/transientrecovery;portalcorrection/hold;503/readiness/adminrecovery;allowlistedSQL/CSV/reconciliation. Controlsresetaftercase; each message uses uniquesyntheticID. Fixedminute quota can matter if you run repeatedly; don't mislabel429 as serverbug.

Maintenance/regression:cutovergood/bad/duplicates;H2migrationtwice,backupsnapshot,nooverwrite,freshrestore,index/schema retained. Additional structural audit validates every R-IDpath,incident/runbook/ticketrequiredfields,OpenAPI schema/examples/APIpaths,mirroredSQL/schema,links and no obvioussecretpatterns. These are meaningful contentcontracts, not a claim of fullstaticanalysis.

Browser:2Playwright tests exercise auth/scopeddisplay,readerwritefail,partnerposting,operatorview,errorfeedback,logoutandmobile390px. Token input password/inmemory; no realcredential screenshot. Browser/IAB unavailable in executionenvironment, so Chromiumfallback explicitly recorded. UI+APIproof supplement each other; no pixel-designclaim.

Release/smoke:health and end-to-end two-sites event/dedup/ACK/reconciliation. Productionvalidation requires actualmandaat/allowedtestdata/config/scope and agreedmonitorwindow. Oracle/AIX/vendorproducts not tested; performancequeryplan is real but scale/SLA/speedup notclaimed. Missing enterpriseidentity/TLS/HA explicitly known.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
