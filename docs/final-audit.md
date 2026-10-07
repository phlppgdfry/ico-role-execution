# Final audit — Job Execution Repository

**Assumption / realistic simulation** voor bedrijfssysteem, rollen, ticket-/incidenthistorie en approvalrecord. Audit beoordeelt de repo, niet iemand zijn dienstverband of daadwerkelijke ICO-geschiktheid. Uitgevoerd testbewijs is afzonderlijk in [verification.md](testing/verification.md).

## Vacancy coverage

35 geparafraseerde clauses zijn gekoppeld aan terugvindbare artefacts in responsibility/skills/evidence matrices en hiring guide. Alle named systems expliciet: IBM P-series/AIX/Oracle/JBoss/iWay/WebFOCUS/Apex; menselijke N/E/F-talen, Office, projectmethode, safety/quality/environment, internal/external team, gebruikers/newcomertraining, rapportage, Kallo/Zeebrugge, wachtdienst en business/vendor/budget. Diploma/arbeidscontext/voordelen zijn geen kunstmatige codebewijsclaim.

## Technical correctness

Echte Java21/Servlet/JDBC-implementatie en WAR, lokale HTTP en signed callback. Atomic state/event/audit/outbox; durable failures, partnerbusiness-key hash/dedup, changedpayload409, scoped SQL vóór200-rowlimit, version/order/location/hold validation. Role actionsserver-side, controls/admin/re-drive/audit bounded. Actual WildFly EE10 deployment and undeploy/redeploy checked; schema/SQL mirrors audited. OpenAPI3.1 route/shape/reference checks supplement actualHTTP tests.

H2 MODE=Oracle does not make it Oracle. DDL/optimizer/backup/productbehaviour remain substitutionlimits. SQL is parameterbound; no arbitrary diagnosticquery orcallbackURL. No claims of distributed exactly-once delivery, enterpriseSLA or performanceimprovement without baseline.

## Operational realism

Ten complete incidents with impact/hypotheses/counterevidence,logs/queries/rootcause/workaround/fix/validation/communication; three problems/5-Whys, three CRQ’s and release1.4.0. Eleven runbooks, twenty varied tickets, workpackages/RACI/budget/portfolio/training/onboarding and eight focused automations. Stories have fictional timestamps and role approvals; actualtest output never substituted for fictional professionalexperience.

Receipt !=businesscommit !=ACK. Redrive ofPROCESSED forbidden; wrongsite/holdrelease considered business/securityboundary. Healthgreen cannot hide pausedworker because backlogage is independently exposed. Restorefresh-target and cutoverkey/fieldgate demonstrate stop/no-go/recovery rather than blind rollback.

## Documentation / consistency

Canonical schema/resources, reviewed SQL mirrors, fixtures and OpenAPI are tested/audited. Commands correspond to workingCLI endpoints. Five Mermaid diagrams reflect one modularmonolith/single active processinginstance plus independentACKdispatcher. Product substitutions list what remains untested. README gives real setup/exploration and hiring guide five-minuterelevance. No dead links permitted by structural audit.

## Corrections actually made

1. Scoped list queries now filter in SQL before displaylimit, avoiding invisibility of older scopedrecords.
2. Request mean metric uses completedrequests, not an unfinished currentrequest as denominator.
3. Separate processor/ACK scheduling prevents slowcallback from blocking newbusinessprocessing.
4. PermanentACK4xx stops in deadletter; explicit regression proves no repeatedbusinessmutation.
5. WAR shutdown closes scheduler/DB; actualundeploy/redeploy checks file-lock/lifecycle boundary.
6. CLI now handles temporary non-JSON container404 duringdeployment; first realrehearsal exposed it.
7. Contract fieldlengths match OpenAPI, including32-char location.
8. Holddecision stored in auditaftervalue without overflowing boundedreasoncolumn.
9. Schemas keep initial migrationrecord rather than resetting timestamp onstartup; actual JVM applytime recorded.
10. HTTPError resources closed; screenshots tokenmasked; no source/secrets in publicrepo.

## Portfolio value / overengineering

Proof follows vacancy rather than technologycount. Real WAR and reusable verticalflow demonstrate development,applicationmanagement,integration,secondline anddelivery. No unnecessary framework,microservices,Kubernetes,cloud orAI. Native Mavenlayout enables professional artifactbuild; no fake APEXexport/OracleDDL claimedrunnable. CSVforecast creates traceable planningproof: fictiveplanned€8000,forecast€8880,+11%; owner must choose scope/time/capacity, not silently acceptdrift.

## UI and QA environment

Functional portal tested withPlaywright because built-inBrowser/IAB unavailable; localdesktop/mobile390px,scopedreads,readerwriteforbidden,partnerpost,operatorview,logout,errorfeedback and no documentoverflow. Python/Maven/browser networkexecution required sandboxpermission; tests then ran outside restrictedsandbox. Actual HTTPcontract runs both JDK adapter and deployedWildFlyWAR. Localtests,CI and recordedproof distinguish eachlayer.

## Explicit remaining boundaries

- Not actual ICO-TOS/productarchitecture orprofessionalexperience; jobselection not assessed.
- H2/nativeOS/in-processmiddleware/SQLreport/HTMLportal substitute Oracle/AIX/IBM/iWay/WebFOCUS/APEX. Productport needs realversions/licences/sandbox/ownerreview.
- No enterpriseidentity/TLS/HA/distributedworker/pool/productionloadbenchmark; local-onlymutationAPI.
- UI lists bounded200 and limitedtaskflow, not a fullTOS. No complete shipping/customs/financeprocess.
- Portalcorrection updates vehicle/audit only; productiondownstreamnotification requires agreedcontract/change.
- Manual full-serverCI downloads267MB and is opt-in; defaultCI tests localadapter. Actualserver testresults separatelyvisible.
- Screenshot/automation/browserproof covers Chromium,not fullSafari/Firefox/accessibilityaudit.
- Narrow structural/known-secret-pattern checks,not comprehensiveCVE/pentestcertification.

These boundaries do not leave important requirements without artefacts; they honestly bound productproof and realauthority. Repo is ready to demonstrate how the role works, with real runnablelab and verifiable operationalthinking.
