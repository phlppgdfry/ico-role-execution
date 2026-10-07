#!/usr/bin/env python3
"""Maintains reviewable operational artefacts and test fixtures, not fake execution evidence."""
from pathlib import Path
import json,shutil,textwrap
ROOT=Path(__file__).resolve().parents[2]
def write(path,body,simulation=True):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    text=textwrap.dedent(body).strip()
    if simulation and p.suffix=='.md':text+='\n\n---\n**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.\n'
    p.write_text(text.rstrip()+'\n')

queries={
'failed-messages':"SELECT id,event_key,site_id,status,attempts,last_error,received_at FROM messages WHERE status IN ('REJECTED','DEAD_LETTER','RETRY_WAIT') ORDER BY received_at DESC FETCH FIRST 200 ROWS ONLY",
'duplicate-records':"SELECT partner_id,event_key,COUNT(*) AS duplicate_count FROM messages GROUP BY partner_id,event_key HAVING COUNT(*)>1",
'recent-errors':"SELECT id,event_key,status,last_error,attempts,received_at FROM messages WHERE last_error IS NOT NULL ORDER BY received_at DESC FETCH FIRST 50 ROWS ONLY",
'reconciliation':"SELECT m.id,m.event_key,'EVENT_OR_ACK_MISSING' AS discrepancy FROM messages m WHERE m.status='PROCESSED' AND ((SELECT COUNT(*) FROM business_events b WHERE b.message_id=m.id)<>1 OR (SELECT COUNT(*) FROM outbox o WHERE o.message_id=m.id)<>1) UNION ALL SELECT m.id,m.event_key,'UNPROCESSED_HAS_BUSINESS_EFFECT' FROM messages m WHERE m.status<>'PROCESSED' AND EXISTS (SELECT 1 FROM business_events b WHERE b.message_id=m.id)",
'slow-query-plan':"EXPLAIN SELECT id,status,received_at FROM messages WHERE status='RETRY_WAIT' AND next_attempt_at<=0 ORDER BY received_at FETCH FIRST 20 ROWS ONLY",
'outbox-status':"SELECT o.message_id,m.event_key,m.status AS business_status,o.status AS ack_status,o.attempts,o.last_error,o.created_at,o.sent_at FROM outbox o JOIN messages m ON m.id=o.message_id ORDER BY o.created_at DESC FETCH FIRST 200 ROWS ONLY"
}
for name,sql in queries.items():
    write(f'database/diagnostics/{name}.sql',sql+';',False);write(f'src/main/resources/diagnostics/{name}.sql',sql+';',False)
write('database/queries/occupancy.sql',"SELECT site_id,partner_id,state,COUNT(*) AS vehicle_count,SUM(CASE WHEN hold_flag THEN 1 ELSE 0 END) AS held_count FROM vehicles GROUP BY site_id,partner_id,state ORDER BY site_id,partner_id,state;",False)
write('database/queries/data-quality.sql',"SELECT v.vin,v.site_id,v.location_id FROM vehicles v JOIN locations l ON l.location_id=v.location_id WHERE v.site_id<>l.site_id OR l.active=FALSE;",False)
write('database/migrations/V002__error_lookup_index.sql',"CREATE INDEX IF NOT EXISTS idx_messages_error ON messages(status,received_at,last_error);\nINSERT INTO schema_version(version,applied_at) SELECT 2,0 WHERE NOT EXISTS (SELECT 1 FROM schema_version WHERE version=2);",False)
schema=ROOT/'database/schema/001-terminal.sql';schema.parent.mkdir(parents=True,exist_ok=True);shutil.copy(ROOT/'src/main/resources/schema.sql',schema)
write('database/README.md','''
# Database operations

H2 2.5.252 / JDBC / MODE=Oracle is the tested lab. It is not Oracle Database and does not prove Oracle optimiser, PL/SQL, RAC, backup or AIX behaviour. Canonical schema: `src/main/resources/schema.sql`; reviewed mirror: `database/schema/001-terminal.sql`. Author script synchronises queries and schema; repository audit compares bytes.

## Tables and invariants

sites/partners/locations are synthetic masterdata. messages is durable business-key journal with UNIQUE(partner_id,event_key), original input and canonical payload hash. deliveries records repeat transport attempts. vehicles carries owner/site/location/state/hold/version and event/processing times. business_events links a message at most once. audit_log records actor, old/new, reason and correlation. outbox is unique per processed message. controls contains explicit lab configuration/faults. schema_version gives migration evidence.

Foreign keys/checks/indexes enforce structure. Worker transaction commits vehicle + event + audit + outbox + processed status together. Timestamp ordering and optimistic version checks avoid silent lost updates. Only one app/worker instance is supported; JVM synchronization is not a cluster lock. Per-request JDBC connection, no enterprise pool. Startup masterdata MERGE does not reset transactional history or controls.

## Diagnostic queries — all read-only

| Query | Purpose | Interpretation |
|---|---|---|
| failed-messages.sql | Open retry/reject/dead-letter | Separate transient error from businessreject; no blanket replay |
| duplicate-records.sql | Business-key duplicates | Empty because unique constraint; delivery duplicates are allowed |
| recent-errors.sql | Last 50 journal errors | Cumulative bounded list, not a time-window failure rate |
| reconciliation.sql | Processed/event/outbox consistency | Empty expected; open ACK status is not missing businesscommit |
| slow-query-plan.sql | Real EXPLAIN plan for queue query | Inspect indexed access; no invented latency improvement |
| outbox-status.sql | Commit/ACK separation | PROCESSED + ACK RETRY_WAIT means only acknowledgement retry |
| occupancy.sql | Current unique vehicles by site/partner/state | Do not count message/delivery rows as vehicles |
| data-quality.sql | Site/location inconsistency | Empty expected; functional rules plus DB constraint boundaries |

Online diagnostics are allowlisted through `/api/admin/diagnostics/{name}`. No arbitrary SQL API. `python3 src/scripts/manage.py failed` and `reconcile` are online. Do not open the file DB from a separate process while the app owns its file lock.

## Offline maintenance

Stop app before file-db migration/backup. DbTool supports a SCRIPT snapshot, fresh-target restore and reviewed migration file inside runtime only. A snapshot is synthetic lab data, not enterprise backup strategy. H2 DDL may auto-commit: schema changes need explicit recovery, not an assumed transaction rollback. Index V002 is additive; rollback can leave a harmless index, whereas data restore requires a fresh destination and explicit validation.
''')

sample=dict(message_id='transport-001',event_key='ARR-001',partner_id='ALPHA',site_id='ZEE',vin='DEMO0000000000001',event_type='ARRIVAL',location='ZEE-A01',event_at='2026-09-28T08:00:00Z',expected_version=0)
fixtures={'arrival':sample,'move':dict(sample,message_id='transport-002',event_key='MOVE-001',event_type='MOVE',location='ZEE-A02',event_at='2026-09-28T08:05:00Z',expected_version=1),'departure':dict(sample,message_id='transport-003',event_key='DEP-001',event_type='DEPARTURE',location='ZEE-A02',event_at='2026-09-28T08:10:00Z',expected_version=2),'duplicate':dict(sample,message_id='transport-001-retry'),'unknown-location':dict(sample,message_id='transport-badmap',event_key='ARR-BAD-MAP',vin='DEMO0000000000003',location='ZEE-A-01'),'kallo-arrival':dict(sample,message_id='transport-kallo',event_key='ARR-KAL-001',site_id='KAL',location='KAL-B01',vin='DEMO0000000000002')}
for name,body in fixtures.items():write(f'edi/samples/{name}.json',json.dumps(body,indent=2),False)
write('edi/samples/malformed.json','{"event_key":"broken",',False)
write('edi/mappings/location-v1.json',json.dumps({'version':'1','rule':'exact active masterdata code; site must match'}),False)
write('edi/mappings/location-v2.json',json.dumps({'version':'2','aliases':{'ZEE-A-01':'ZEE-A01','ZEE-A-02':'ZEE-A02','KAL-B-01':'KAL-B01','KAL-B-02':'KAL-B02'},'constraint':'alias target must exist, be active and match site'}),False)
write('edi/validation/profile.md','''
# Synthetic EDI profile

The actual ICO EDI standard/transport is unknown. This JSON contract demonstrates EDI concepts, not EDIFACT compliance. All nine fields are required; extra fields rejected. message_id is transport identity, event_key is partner-specific business identity. A retry may change message_id while preserving the business payload. Changed payload under the same event_key returns 409. IDs are bounded; synthetic vin is 17 uppercase alphanumerics, not an official VIN/checkdigit implementation.

event_at must parse as ISO instant and be at most five minutes in the future. expected_version is integer ≥0. Initial ARRIVAL requires 0; transitions require current version and increasing event time. MOVE/DEPARTURE require active vehicle, same site/partner and active masterdata location. DEPARTURE blocked by hold and requires current location. Re-arrival is allowed only for departed vehicle with current expected version and later timestamp. Business rejects are asynchronous and visible in journal, not automatically retried.

Mapping v1 requires exact location code. v2 supports only the two prefixes represented by reviewed examples, then checks masterdata again. No catch-all location or silent coercion. Arrival/move/departure samples form one ordered demo; unknown-location uses a separate vehicle. Repeating the same arrival returns duplicate receipt rather than creates another vehicle.
''')
write('edi/troubleshooting/received-not-processed.md','''
# EDI received but not processed

## Symptoms / impact
202 receipt exists; operational status absent. A receipt proves durable acceptance, not commit. Ask event key, partner/site, expected task and physical deadline.

## First checks
Look up receipt ID using partner token or scoped journal. RECEIVED: worker/backlog; RETRY_WAIT: transient dependency with attempt/next time; REJECTED: contract/business error; DEAD_LETTER: retries exhausted; PROCESSED: inspect outbox/report/display rather than replay business.

## Commands / queries
`python3 src/scripts/manage.py failed`; `request ADMIN GET /api/admin/diagnostics/outbox-status`; `reconcile`. SQL references: failed-messages, recent-errors, reconciliation. These commands are read-only. Do not directly UPDATE status.

## Logs / causes
message.received → message.rejected/retry/committed → ack.failed/sent, joined by system message ID. Common labs: worker_paused, dependency_unavailable, UNKNOWN_LOCATION, VERSION_CONFLICT, OUT_OF_ORDER, HOLD_ACTIVE. TransportID may change across duplicate deliveries.

## Resolution / escalation
For temporary failure remove the cause within mandaat and wait for bounded retry. For permanent reject fix contract/masterdata/mapping through CHG-003, then admin redrive with reason only if no businesscommit. PROCESSED cannot redrive. ACK failure retries only outbox; callback is idempotent. Escalate safety/data/security ambiguity to business/IT owner before correction.

## Prevention
Contract samples, negative tests, oldest-age alert, commit/ACK separation, unique keys and training. Validate actual vehicle outcome, business_events/outbox reconciliation and partner receipt before closing.
''')

write('docs/requirements/business-requirements.md','''
# BR-001 — Controleerbare terminaldatastroom

## Vage vraag → probleem
“We willen dat partnerberichten sneller en zonder dubbel werk in het terminalscherm komen.” Analysevragen: welke taak blokkeert, hoeveel unieke voertuigen/events, welke vestiging/partner, wat is ontvangen versus verwerkt, welke fysieke status klopt? Fictieve as-is: e-mails en handmatige herinvoer, geen gezamenlijke correlation-ID, transporttimeout leidt tot dubbel verzenden. Niet als ICO-feit lezen.

## Gewenste situatie / stakeholders
Operations kan locatie/status/audit vertrouwen. Partner krijgt een receipt en later business-ACK. Development officer kan eerste foutgrens en backlog onderzoeken. IT supervisor autoriseert change/release binnen scope; business approver beslist fysieke vrijgave. Service Desk verzamelt scope en eskaleert naar tweede lijn; leveranciers leveren contract/mapping- en runtimesupport. Zie RACI.

## Business outcomes
BR1: één business-effect per partner/eventkey. BR2: zichtbare verwerking en verklaarbare afwijzing. BR3: beide sites geïsoleerd correct. BR4: correcties met actuele versie, reden en audit. BR5: hold beschermt vertrek, vrijgave vraagt bevoegde beslissing. BR6: herhaalbare recovery en release-evidence. BR7: rapporten tellen unieke voertuigen en gebruiken afgesproken snapshot/definitie.

Geen verzonnen ROI/SLA. Labdoelen in NFR zijn testbare eigen ontwerpkeuzes. Acceptatie betekent succesvolle én negatieve taaktests plus geaccepteerde beperkingen, geen mooi scherm alleen. Requirementscope: synthetische voertuigen en twee partners; niet shipplanning, finance, douane of echte PDI/ERP.
''')
write('docs/requirements/functional-specification.md','''
# Functional specification

| ID | User story / rule | Edge cases |
|---|---|---|
| FR01 | Als partner stuur ik event met mijn site/partner-scope | Spoofing 403; syntax/unknown keys 400; 16 KiB limit 413 |
| FR02 | Als partner krijg ik receipt-ID en status | New 202; same business payload 200 duplicate; changed payload 409 |
| FR03 | Als operations volg ik durable journal | RECEIVED/RETRY_WAIT/PROCESSED/REJECTED/DEAD_LETTER zichtbaar |
| FR04 | Worker past geldige transitions atomisch toe | Invalid site/location, old version/time, ownership of hold blokkeren |
| FR05 | Callback krijgt pas na commit HMAC-ACK | Timeout retry zonder businessreplay; permanente 4xx naar dead letter |
| FR06 | Operator corrigeert locatie | Reader 403; invalid site 400; old version 409; reason verplicht |
| FR07 | Operator legt hold vast; approver geeft vrij | Release ADMIN + decision_ref; versiecheck/audit; geen fysieke claim |
| FR08 | Admin wijzigt labcontrols/re-drives | Alleen gelabelde sandbox; processed message nooit re-drive |
| FR09 | Reader/partner krijgt correct scoped report | Count vehicles, not deliveries; two sites and partner-scope |
| FR10 | Tweede lijn diagnosticeert read-only | Query-name whitelist, no arbitrary SQL, admin only |
| FR11 | Release owner bouwt en valideert WAR | Hash/version, config/secrets apart, rollbackcompatibiliteit |

Reception, domaincommit and callbackdelivery zijn aparte fasen. Een fout in ACK mag geen vehiclemutatie ongedaan maken. Portaalfeedback houdt token in geheugen, toont fouten en gebruikt dezelfde serverautorisatie als direct API-verkeer.
''')
write('docs/requirements/technical-specification.md','''
# Technical specification

Router handles method/path/auth/body/rate/correlation and maps ApiError to public error codes. TerminalService owns validation, scoped reads, transaction transitions, correction and authorized redrive. Business processor and ACK dispatcher independently attempt one eligible item every 200ms; slow ACK does not block processing. Database owns prepared statements, bounded queries and schema. LocalServer and TerminalServlet are adapters for the same implementation; SecurityHeaders protects WAR responses. No Spring/JPA requirement invented.

Canonical businesshash covers eventkey, partner, site, vin, type, mapped input location string, normalized instant and version; transport message_id excluded. Unique DB key prevents semantic duplicate; JVM service synchronization handles concurrent requests in the supported single instance. Original payload kept for diagnosis. Changed eventkey is not automatically the same event: partner must follow contract.

Worker uses current location mapping version, verifies active location/site and current vehicle version under transaction row lock, then vehicle/event/audit/outbox/status commit. Business error rolls back before journalling reject. Transient dependency fault yields bounded retry 1/2/4/8/16 seconds, at most five processing attempts. No production jitter strategy claimed; additional production burst/load control belongs in capacitydesign.

HTTP ACK dispatcher has 1s connect/2s overall timeout, no redirects, loopback target allowlist and HMAC SHA256. 2xx accepted; 4xx permanent, other errors bounded. Outbox plus idempotent callback tolerate response loss. Callback is actual local Python HTTP server, not a fictional external success. Database/script failure cannot produce a false healthy business outcome.

Controls, schema, mapping and artefact versions are distinct release dimensions. Database.schema init does not migrate away user data; additive V002 is separately reviewed/executed offline. File DB locked by one process. Shutdown closes worker then DB, including WAR undeploy. Production extensions require real Oracle JDBC/pool, identity/TLS, distributed worker claim and platformprocedures; see substitutions.
''')
write('docs/requirements/non-functional-requirements.md','''
# Non-functional requirements — lab targets

| ID | Requirement | Verification / boundary |
|---|---|---|
| NFR01 | No embedded production credential; five distinct ≥24-char bearer secrets | Config refusal, generated .env 0600, secret pattern audit |
| NFR02 | DB commit atomic and repeat transport harmless | JUnit atomicity/concurrent duplicate + HTTP duplicate |
| NFR03 | Bounded request/DB/callback resources | 16 KiB body, 120 actor requests/minute, 5s query, 1s connect/2s ACK |
| NFR04 | Scoped access before list limit | SQL site/partner filter before 200-row display limit; detail 404 outside scope |
| NFR05 | Durable failure/retry state | File journal and restart test; no in-memory-only message queue |
| NFR06 | Evidence without token/rawpayload logs | JSON event/correlation/error/status, audit for mutations |
| NFR07 | Traceable releases and safe recovery | Actual WAR hash, checks, new-target snapshot restore |
| NFR08 | Synthetic-data-only / loopback | Default local ports, callback and CLI allowlist; no TLS claim |
| NFR09 | Operational detection | Open failures, oldest age, queue and ACK alerts; measured metrics only |
| NFR10 | Reproducibility | Java 21/Maven/Python commands and GitHub CI; actual WildFly lab test recorded |

Lab has no guaranteed availability/SLA, no HA, no enterprise pool, no production-scale performance benchmark. List views are bounded at 200, diagnostic/error views at 200 or 50; aggregate reports/reconciliation query all applicable records. API rate-limit is fixed-minute actor quota, no distributed limiter. These boundaries are requirements, not hidden omissions.
''')
write('docs/requirements/acceptance-criteria.md','''
# Acceptance criteria / edge cases

| AC | Given / When / Then | Automated proof |
|---|---|---|
| AC01 | Partner sends valid initial event → 202 and durable RECEIVED → worker PROCESSED | acceptedReceiptIsNotCommit, atomicVehicleEventAuditAndOutboxCommit, HTTP 01 |
| AC02 | Same key/payload sent concurrently/new transport-ID → one effect and duplicate receipts | concurrentDuplicateRequestsRemainUnique, HTTP 02 |
| AC03 | Same key/different location → 409 and no extra effect | changedPayloadWithSameKeyConflicts |
| AC04 | Bad shape/type/date/extra field → 400; oversized body → 413 | fieldsTypesDatesAndUnknownKeysValidated, routerHandlesAuthRateSizeAndRecovery |
| AC05 | Unknown location accepted then rejected → no vehicle/outbox, reviewed mapping+redrive succeeds | unknownLocationRejectsWithoutPartialVehicleOrOutbox, HTTP 03 |
| AC06 | Temporary dependency failure → retry; five failures → dead letter, then controlled recovery | transientFailureRetriesAndAttemptLimitDeadLetters, HTTP 04 |
| AC07 | Callback lost after commit → retry ACK, no new event | lostAckDoesNotReplayBusinessMutation |
| AC08 | Scope spoof/detail outside scope → 403/404 | partnerCannotSpoofScope, HTTP 02 |
| AC09 | Old version/time → business reject; correction requires correct role/reason/version | staleVersionAndOutOfOrderAreBusinessRejects, HTTP 05 |
| AC10 | Active hold → departure blocked; release needs admin+decision | safetyHoldBlocksDepartureAndReleaseRequiresDecision |
| AC11 | Both sites / reports count distinct current vehicles | reportCountsVehiclesNotDeliveriesAndHandlesBothSites, HTTP 01/07 |
| AC12 | Admin diagnostics known name works, unknown denied, reader denied, reconciliation empty | HTTP 07 |
| AC13 | WAR deploy → same HTTP contract, no leaked worker/DB on undeploy | WildFly acceptance + undeploy/redeploy evidence |

UAT script: operator finds vehicle, uses current version, corrects to active same-site location with reason, sees version/audit; reader direct write fails; approver discusses physical hold separately. Trainer asks user to repeat task and explain what 202 means. Production validation must be separately scoped; these are lab gates.
''')
write('docs/requirements/project-plan.md','''
# Technical project plan / work packages

Scope: reliable partner event → terminal record → report → ACK plus operational controls. Out of scope: real ICO interfaces, hardware, enterprise identity, ship planning and high availability. Method: businesscase, staged delivery, workpackages, acceptance and escalation tolerances (PRINCE2-compatible thinking; no certificate claim).

| WP | Output / owner (simulated) | Dependency | Acceptance |
|---|---|---|---|
| WP1 | Business rules / key user + analyst | Stakeholder interviews | BR/FR and safe hold decision accepted |
| WP2 | Contract/schema / developer | WP1 | Constraints + contract negative tests |
| WP3 | Worker/outbox / integration partner | WP2 | Duplicate/timeout/partial-commit tests |
| WP4 | Portal/report / app team | WP2 | Role/version UAT, correct vehicle counts |
| WP5 | Release/recovery / officer + runtime owner | WP3/4 | WAR deploy, hash, smoke and restore rehearsed |
| WP6 | Training/operations / officer + Service Desk | WP5 | Runbooks, teach-back, handover and alertowner |

Milestones: M1 acceptance definition; M2 vertical flow; M3 failure lab; M4 UAT and recovery; M5 lab release/nazorg. Risk tolerances are simulation choices: escalate ≥10% forecast cost drift, missing safety/data gate immediately, critical acceptance failure as no-go. Workpackage acceptance differs from developer-complete. Actual fictive capacity/budget numbers in operations/portfolio, never claimed as ICO budget.
''')

write('docs/architecture/decisions.md','''
# Architecture decision records

## ADR-001 — One modular monolith
Context: role cares about reliable delivery and core/integration understanding, not service count. Decision: Java router/service/worker/JDBC in one deployable WAR. Consequence: low setup cost, cohesive transaction; only one active workerinstance. Alternative Kafka/microservices rejected without scale requirement.

## ADR-002 — H2 instead of Oracle in local execution
Decision: real relational constraints/transactions and Oracle-compatibility mode; explicitly not Oracle implementation. Consequence: operational concepts testable without license/credentials. Oracle port needs datatype/sequence/SQL/locking/plan/backup review, actual JDBC and product UAT. Do not market H2 tests as Oracle test coverage.

## ADR-003 — Durable outbox
Reason: ACK may fail after businesscommit. Decision: queue ACK atomically with effect and retry independently. Consequence: at-least-once ACK; partner receiver deduplicates ack_id. No exactly-once-network-delivery claim.

## ADR-004 — Separate transport and business keys
Retry transport-ID may change. Decision: dedup on partner/event_key plus canonical business hash. Consequence: changed business payload is conflict; transport attempts can repeat visibly without new event.

## ADR-005 — Local-only fault controls and credentials
Testable failure controls require admin, audit, allowlist and loopback. Not production incident tooling. No public demo with mutation keys; no OAuth/SSO implementation claim. Secrets runtime-only.

## ADR-006 — Genuine WAR, fast local adapter
Both adapters reuse Router/TerminalService. Local development can run on JDK with no server install; WildFly lab verifies Servlet mappings/lifecycle separately. Current tested target is EE10 WildFly distribution 41.0.1, not asserted ICO version.
''')
write('docs/architecture/component-catalogue.md','''
# Application modelling / component catalogue

| Component | Owner / purpose | Input/output | Failure / dependency | Version / evidence |
|---|---|---|---|---|
| Inbound API/router | Officer/app team | Bearer event → receipt/error | Auth/rate/shape and DB availability | App 1.4.0, OpenAPI, HTTP tests |
| TerminalService | App team | Validated event → atomic state/audit | Masterdata/version/hold/transaction | Source + JUnit |
| Durable journal | Data owner | Original payload/hash/status | Disk/locks/integrity | H2 schema1 + additive2 |
| Worker/mapping | Integration partner | Pending → processed/reject/retry | Current mapping/dependency control | mapping1/2 + fixtures |
| Outbox/dispatcher | Integration team | Committed event → signed ACK | Callback/TLS production port/retry | HMAC + timeout test |
| ACK simulator | External partner role | HMAC payload → idempotent receipt | Availability/secret | Python mock, loopback |
| Portal | Business key user/app team | Role task → audited correction | API availability/version | HTML/JS, HTTP/UI acceptance |
| Reporting | Business data owner | Vehicles → grouped SQL/CSV | Wrong definition/snapshot | Occupancy query/reconciliation |
| Runtime | Runtime owner | WAR/config → running servlet | Java/container/lifecycle | WildFly EE10 lab + local adapter |
| Controls | Lab approver | Scoped config/fault → audit | Not production mechanism | Admin-only endpoints |

Each release changes the manifest, not just the WAR. Review compatibility between schema, mapping, portal and partner contract. Server inventory for actual ICO remains unknown. OS/hardware/Oracle/productownership must be validated during onboarding.
''')
write('docs/architecture/lifecycle-review.md','''
# Lifecycle review / IT evolutions

Observed 7 October 2026: official WildFly downloads offer 41.0.1 and a separate EE10 distribution. The lab uses EE10 so Servlet6 WAR semantics remain controlled; no assumption that ICO uses this release. Dependencies pinned to verified Maven metadata: H2 2.5.252, Jackson2 2.22.3, JUnit6 6.1.3, compiler3.16 (stable instead of beta4).

Review questions: support horizon/security patches, Oracle/JBoss/AIX compatibility, productlicensing, vendor constraints, data migration, team skills, test environment and total ownership cost. A modern release is not automatic business justification. Proposed decision: keep current working vertical flow, establish product/version inventory with runtime owner, assess required Oracle/JBoss product port through impact/test/rollback workpackage. No unnecessary cloud/containerplatform.

Sources: [WildFly downloads](https://www.wildfly.org/downloads/), [WildFly guide](https://docs.wildfly.org/39/Getting_Started_Guide.html), [H2 features](https://h2database.com/html/features.html), [Jakarta servlet lifecycle](https://github.com/eclipse-ee4j/jakartaee-tutorial/blob/master/src/main/asciidoc/servlets/servlets002.adoc). Context7 resolved WildFly only to Elytron (unsuitable), then Jakarta EE tutorial was fetched. No Elytron-specific auth implementation inferred.
''')

write('docs/systems/platform-substitutions.md','''
# Product/platform substitution and proof boundary

| Vacancy system | Working lab / concrete artefact | What this proves | What it does not prove |
|---|---|---|---|
| IBM P-series | Platform/OS/app ownership diagram + capacity escalation | Layer boundaries and evidence requirements | Hardware, HMC, LPAR or SAN administration |
| AIX | macOS/Linux local Java + AIX transition checklist | Unix/resource/log concepts | AIX command correctness, root/patch/HA practice |
| Oracle | H2 JDBC/Oracle-mode, schema, queries, constraints | SQL/transactions/reconciliation concepts | Oracle-specific syntax/performance/backup/PLSQL execution |
| JBoss | Real WAR deployed to WildFly EE10 lab | Servlet/lifecycle/deploy/recovery integration | ICO JBoss variant/version/cluster/config |
| iWay | Actual worker/mapping/outbox/HMAC integration | Contract/mapping/retry/ACK and diagnosis | Licensed iWay tooling/adapter administration |
| WebFOCUS | Actual grouped SQL/CSV report and reconciliation | BI definitions, datalineage and testing | WebFOCUS syntax/administration/runtime |
| Apex | Actual audited correction portal + portingplan | Business validation/authorization/task UAT | Oracle APEX installation or imported application |

Linux/macOS is used as local simulation environment; the target vacancy explicitly names AIX on IBM P-series. Do not copy Linux-specific troubleshooting commands into an AIX production runbook without checking the exact version and approved procedures. Find OS/process/disk/permission evidence with platformowner. App/DB fixes do not confer hardware mandaat.

Oracle port checklist: Oracle JDBC service/pool configuration; datatypes (BIGINT/BOOLEAN/CLOB equivalents by version), sequences/identity, MERGE/schema syntax, constraint/index names, locking/order-by/fetch compatibility, prepared params/date handling, EXPLAIN via DBA, backup/restore and migration guards. H2 MERGE KEY and IF NOT EXISTS are not advertised Oracle DDL. Do not run lab schema blindly in Oracle.

Enterprise port checklist: identityprovider/SSO/role mapping, TLS, proper secrets/vendortoegang, retained audit, agreed metrics/SLA, clustered queue ownership, transactional business API boundary and real supportprocedure. Local role token is not enterprise identity.
''')
write('docs/systems/apex-porting-plan.md','''
# Apex — assumed Oracle APEX: porting work package

Vacancy says Apex alongside Oracle; productinterpretation remains unconfirmed. No fake APEX export that cannot be imported/tested. The working HTML portal demonstrates the requested behaviour; this document specifies actual APEX work if confirmed.

Target pages: scoped vehicle report, detail/current version, location correction with reason, audit inspection for authorized owner. Regions/items: VIN, site/partner, location select from active same-site masterdata, expected_version and reason. Server-side validations and authorization schemes required; hidden buttons alone insufficient. Use existing TOS/API boundary if direct DB ownership would violate systemcontract.

Request route for actual Oracle APEX may be browser → ORDS/weblaag → APEX engine/PLSQL → Oracle. ORDS is not named in vacancy and is not assumed to run on the JBoss path. APEX session is not permanently the same DB session. Auth/productversion/workspace/deployment/export format must be confirmed.

Acceptance: reader direct correction denied; wrong site/code fails without change; stale version asks reload; successful correction records actor/old/new/reason/time; key user performs task without instructor. Porting evidence required: actual export/import, productversion, authorized sandbox, automated/manual role tests and deployed flow. Until those exist the repository proves task design and equivalent implementation, not APEX productexperience.
''')

write('docs/integrations/partner-contract.md','''
# Partner contract / interface ownership

Owner roles: partner sender owns valid business event/key; integration team owns mapping, receiptjournal, processing and ACK; business owns transition/hold definition; runtime/data owners support resources. Real vendor/standard unknown. JSON schema in OpenAPI is canonical external contract; edi samples are synthetic testfixtures.

Transport POST /api/messages uses partner bearer and strict site/partner scope. 202 = received durably, not processed. GET receipt follows status. 200 duplicate may refer to RECEIVED, PROCESSED or rejected prior event; never interpret it as new businesssuccess. 409 idempotency conflict requires sender investigation, not new key to hide inconsistency. 400/403/413 nonretryable without correction; 429 obey Retry-After and preserve same business key; 5xx/timeout retry bounded with same key and unchanged payload.

Client timeout after reception may repeat safely. Business processing uses 5 attempts, exponential 1–16s delay for the explicitly transient dependency; permanent rules become REJECTED. Admin redrive requires reason and is forbidden for PROCESSED/RECEIVED. Callback comes after commit, is signed over exact UTF-8 body, and uses stable ack_id. Receiver persists dedupreceipt before returning 200. ACK network loss can cause duplicate delivery, not duplicate businessmutation.

Partner data model: arrival/version0; current-version move; current-version departure with location/hold rules. Event timestamp must increase for an existing vehicle. A retry does not change timestamp/version/location. Codechange/mapping requires sample exchange, version decision, acceptance and coordinated release. Evidence pack includes system receipt ID, partner/event key, transport ID, timestamp/zone, mappingversion, first failure and expected result; no tokens/raw sensitive payload in email.

External networking/TLS not verified in this lab. Callback allowlist deliberately permits only localhost/127.0.0.1; production integration needs HTTPS, certrotation, identity/replay policy and actual vendor agreement. Browser cross-origin mutation is not enabled.
''')

write('monitoring/alerts/thresholds.json',json.dumps([
dict(name='processing_stalled',metric='oldest_pending_seconds',threshold=30,severity='WARNING',owner='integration-oncall',action='Check worker/last success; do not bulk replay'),
dict(name='queue_depth',metric='messages_received',threshold=50,severity='WARNING',owner='application-owner',action='Compare input volume and consumption'),
dict(name='open_rejections',metric='messages_rejected',threshold=1,severity='TRIAGE',owner='integration-owner',action='Inspect error codes; expected training rejects may be acknowledged'),
dict(name='exhausted_retries',metric='messages_dead_letter',threshold=1,severity='CRITICAL',owner='second-line',action='Determine impact and authorized redrive'),
dict(name='ack_exhausted',metric='ack_dead_letter',threshold=1,severity='CRITICAL',owner='partner-contact',action='Business may be committed; repair ACK only')],indent=2),False)
write('monitoring/dashboards/operations.json',json.dumps(dict(source='/api/metrics',panels=['messages_received','messages_retry_wait','messages_rejected','messages_dead_letter','oldest_pending_seconds','ack_pending','ack_dead_letter','http_requests','http_errors','mean_request_ms'],simulation=True,notes='Actual instantaneous/cumulative measurements; not fabricated uptime, p95 or enterprise DB connection counters'),indent=2),False)
write('docs/monitoring/observability.md','''
# Observability / proactive detection

JSON logs: timestamp UTC, event, correlation_id, method/path/status or message/error/attempt/version/site. Request correlation supplied safe [A-z0-9_-] or UUID; message worker/ACK logs use stable receipt ID. Never log bearer/secret/body. audit_log is separate: actor/action/entity/before/after/reason/time. stdout goes to runtime/app.log or WildFly server.log; lifecycle/runtime errors remain distinguishable.

Metrics are actual database statuses, oldest pending age, open/exhausted ACKs and cumulative request/error count plus mean completed request duration. No fabricated p95, poolconnections or availability. 200-row UI list is not full reconciliation; SQL aggregate/consistency query covers all rows. Thresholds are local training targets, not ICO SLA. Open rejection count is triage inventory, not an interval failure rate; expected labs intentionally trigger it.

Health GET /health reads DB and reports app version/readiness. Forced API fault returns 503; worker pause leaves technical health green, so backlog/last businessoutcome must also be checked. “Green process” is not “healthy chain”. Dashboard schema defines panels; portal shows subset, CLI alerts uses full metrics. Log summary automates grouping but never concludes root cause by error count alone.

Example: oldest pending ≥30s warns worker-oncall; investigate reception/last commit/controls. Dead letter ≥1 raises critical review; businessimpact still determines incidentseverity. Metrics polling 120 actor requests/minute quota shared by role; use appropriate interval, not uncontrolled refreshloop. Production alert suppression/window/escalation and real instrumentation require agreed workload measurements.
''')

write('docs/security/security-baseline.md','''
# Security baseline

Authentication: five distinct random bearer tokens generated into runtime/.env (0600), minimum 24 chars, comparison via MessageDigest.isEqual. No production/default secrets. Authorization: PARTNER submits own partner/site and reads own rows; READER reads/report/metrics; OPERATOR corrects location and sets hold; ADMIN releases hold with decision_ref, re-drives failures, views audit and controls. This is a lab rolemodel, not employment mandate or enterprise SSO.

Least privilege: role/server/object scope enforced, outside detail scope 404. SQL filters precede list limits. Bound queries and fixed diagnosticallowlist; no arbitrary SQL endpoint. 16 KiB requests, fixed minute actor quota and bounded DB/callback timeouts. Secrets never in URL/log/bodyexamples or Git; portal keeps token only in memory. Clear action removes token/loaded data. Runtime directory private, file DB has no TCP listener and empty embedded sa password is acceptable only under local file/OS boundary.

Integrations: exact payload HMAC SHA256, callback allowlisted to loopback, redirects denied, receiver dedups stable ack_id. HTTP allowed only in local lab. Production needs TLS/cert/trust, identityprovider, keyrotation, serviceaccounts with owner/expiry, storageencryption/retention and incidentprotocol. No security certification or penetration-testclaim.

Sensitive data: synthetic IDs only; real VIN/customerdata must not be added. Logs deliberately omit payload/secrets; audit access adminonly. Token leak: stop affected lab, regenerate runtime credentials under approved local owner, restart both services and retest roles/HMAC. No actual notifications or submissions to ICO.

Threats: scope spoofing (deny), duplicate/concurrent event (unique/hash), changed payload (409), unauthorized direct UI bypass (server deny), secret log exposure (no token logs), oversized body/quota, ambiguous physical release (businessapprover). Remaining lab limits: no TLS, MFA, sophisticated tokenmanagement, HA, distributed limiter or hardened internet exposure. Do not host this mutation API publicly.
''')
write('docs/security/security-review-checklist.md','''
# Security review checklist

- [ ] Random distinct tokens, no real credentials in fixtures/Git/history.
- [ ] Runtime/.env permissions 0600; directory private; no public listener.
- [ ] Every mutation checks role and objectscope on server, negative tests pass.
- [ ] Partner BETA cannot read/submit ALPHA or ZEE objects.
- [ ] Location/version/reason validation and business hold decision audited.
- [ ] SQL prepared; diagnosticnames allowlisted; no arbitrary external callback URL.
- [ ] HMAC bad signature denied; same ack_id duplicate safe.
- [ ] Logs/source/screenshots contain no tokens or real data.
- [ ] WAR security filter/CSP/nosniff and no-store verified.
- [ ] Body/rate/timeout limits fit lab; production gaps explicitly assessed.
- [ ] Snapshot access/integrity/retention assigned; restore uses fresh target.
- [ ] Unclear exposure or unsafe physicalstatus escalates to security/businessowner.

This checklist supports review; a checkbox alone is not proof. Attach testname/log/query or reviewer decision. All approver identities in sample records are fictive roles, not actual ICO approvals.
''')
write('docs/security/safety-quality-environment.md','''
# Quality / safety / environmental support

Vacature vraagt ondersteuning van kwaliteits-, veiligheids- en milieumanagement. Concrete interne normen/certificaten onbekend. Simulatie: softwarevrijgave mag geen fysieke toestemming suggereren zonder businessbesluit; holds blokkeren vertrek, audit maakt correcties traceerbaar en operator kan hold niet zelfstandig verwijderen. Een IT-medewerker is niet automatisch operationeel releaseowner.

Quality gate: receipt/event/outbox reconciliation, locatie-/site-validatie, negatieve UAT en reproducerbare release. Veiligheidsworkaround moet eigenaar, beperkingen, einddatum en latere reconciliatie hebben. Bij statusconflict fysieke handeling pauzeren via bevoegde operationsowner, niet blind UPDATE toepassen. Milieu: betrouwbare rapportdefinities/efficiënte informatie kunnen processen ondersteunen; repo berekent geen fictieve emissie-KPI of certificering.

Voorstel verbetering: detecteer herhaalde statuscorrecties per proces en bespreek bronoorzaak met key user; automatiseer read-only controles zodat minder handmatige herinvoer nodig is. Effect eerst echt meten, geen verzonnen percentages.
''')

write('docs/role/role-operating-manual.md','''
# Role operating manual — zo voer ik de rol uit

## Morning routine
08:30 overdracht/incidentowner controleren; veiligheidsimpact en open productiehandelingen bespreken. Health plus backlog/oldest pending en ACK-inventory bekijken, niet alleen groen proces. Service Desk-ticket moet site/partner/tijd/expected-versus-actual/repro/ID bevatten. Actieve incidenten vóór projecten op impact/urgentie prioriteren. Lees vendoracties en releasekalender; reserveer capaciteit voor interrupts.

## During the day
Eén owner per ticket, meerdere hypotheses met onderscheidend bewijs. Volg gebruiker → API → journal → mapping → commit → ACK → rapport. Read-only checks eerst; veranderingen met mandaat/CRQ en herstelplan. Behoeftenanalyse begint bij taak/uitzondering; technical specs omvatten roles, data, interfaces, foutpaden, acceptance en afhankelijkheden. Vendor krijgt werkpakket en objective acceptance, geen “maak het werkend”. UAT met key user zelf laten uitvoeren; documentatie/training zijn deliverables.

## End-of-day checks
Geen half deployment zonder overdracht. Backlog/difference sets/ACK na herstel opnieuw meten. Tickets sluiten pas na businessvalidatie; onzekere oorzaak naar problem met owner. Vastleggen: actie/tijd/uitkomst, open risico, volgende stap/eigenaar/update. Kritieke credentials/toegang/escalatiedekking vóór wachtdienst controleren. Geheimen niet in werknotities.

## Weekly responsibilities
Portefeuille en accepted delivery tegenover baseline; capacityforecast/actual/remaining cost; afwijkingen vroeg met opties melden. IT/businessweekrapport heeft resultaat, impact/risico, besluit, owner en datum. Releaseafhankelijkheden tussen app/schema/mapping/partner bevestigen. Eén terugkerend incident voor prevention kiezen; één runbook/quick guide valideren met collega. Taal N/E/F op doelgroep afstemmen.

## Monthly responsibilities
Componentcatalogus/lifecycle/supportstatus, vendorservice/contract en capacitytrend bespreken. Rehearsal van herstel/backup en één end-to-end foutscenario. Audit van toegangsrechten/secretowners/retention met echte securityowner. Projecttoleranties en trainingsplan bijwerken. Datakwaliteit/rapportdefinities met business bespreken; tijdwinst alleen met baseline claimen.

## Critical-event behaviour
Veiligheid/impact eerst, incidentowner en vaste updatecadans. Beperk scope, preserveer evidence, geen parallelle tegenstrijdige fixes. Escaleer data/security/mandaatgrens en specialistbehoefte vroeg. Workaround heeft owner/beperking/einddatum/reconciliatie. Stop/no-go bij onbekende migratiestaat of ontbrekend recoverybewijs. Communiceer feit/onbekend/actie/volgende update; geen onbewezen ETA. Root cause vereist bewijs en tegenhypothese, geen schuldnaam.

## Ownership
Ik ben verantwoordelijk voor gecontroleerde uitkomst binnen afgesproken domein, niet alleen mijn codetaak. Ik volg acceptance, training, nazorg en overgedragen acties. Budget-/go-live-/fysieke-vrijgavemandaat komt van bevoegde owners. Alle daadwerkelijke ICO-eigenaren, versies, tools en rooster moeten intern bevestigd worden.
''')
write('docs/role/top-performer-guide.md','''
# Top employee behaviour

| Dimensie | Gemiddelde taakuitvoering | Sterke uitvoering / bewijs |
|---|---|---|
| Ownership | Ticket dicht bij service restart | Business/data/ACK gevalideerd, problemactie met owner |
| Communicatie | Technische dump | Businessimpact/besluit en technische evidence apart |
| Preventie | Zelfde workaround herhalen | Trigger/oorzaak testen, regressie/alert/contract verbeteren |
| Documentatie | Notitie in eigen hoofd | Runbook bruikbaar door volgende wachtdienstcollega |
| Automatisering | Iedere dag dezelfde handcheck | Read-only script met duidelijke exitcodes, falsifiable output |
| Businessdenken | Scherm werkt | Fysieke taak/status/owner, veilig holdbesluit en adoptie |
| Betrouwbaarheid | Onzekere ETA beloven | Vroege forecast/risico en realistische updatecadans |
| Technische diepte | Productnamen kennen | Keten/atomiciteit/idempotentie/recoverygrens verklaren |
| Stakeholder trust | Reactief antwoorden | Werkpakketten, acceptance, besluit- en actielog |

Top 10% is gedragsmodel, geen gemeten ICO-ranking. Maandvoorbeeld: een ACK-problem niet alleen oplossen maar onderscheid commit/ACK zichtbaar maken, test voor response-loss toevoegen, vendorcontract aanscherpen en Service Desk trainen. Held die alles alleen oplost zonder overdracht creëert afhankelijkheid; betrouwbare medewerker maakt collega’s effectief.
''')

# Ten full incident records use distinct evidence, risk and resolution; sample timeline is always fictive.
incidents=[
dict(id='INC-001',slug='worker-stalled',title='Partnerberichten ontvangen maar niet verwerkt',severity='SEV2',impact='ALPHA ZEE-aankomsten zichtbaar als receipt maar ontbreken in operationeel beeld; fysieke deadline door key user te bevestigen.',systems='API, message journal, worker, portal',symptoms='202 receipt, RECEIVED blijft staan; oudste backlog groeit terwijl /health 200 geeft.',hypotheses='H1 worker gepauzeerd; H2 tijdelijke dependencyfout; H3 mappingreject. RECEIVED zonder attempts spreekt tegen H2/H3.',investigation='Zelfde receipt/site volgen. Metrics worker_paused=true. Geen message.retry/rejected/committed voor receipt. Controls-audit koppelt pause aan labconfig; database bevat input maar geen business_event/outbox.',logs='message.received aanwezig; geen message.committed; request.completed 200 voor health. Illustratieve eventnamen, echte logs apart.',queries='failed-messages, reconciliation en SELECT status,attempts FROM messages; status RECEIVED is niet in failed-query, dus ook scoped journal bekijken.',root='In deze scenariohistorie bleef worker_paused aan na training; healthcheck controleerde DB/API maar niet businessvoortgang.',workaround='Businessowner bewaakt betroffen taken en zet geen tweede inputstroom op zonder reconciliatie. Queue blijft durable, geen data-update.',fix='Admin zet worker_paused=false met audit, monitor oudste leeftijd en commituitkomsten; alert op backlogleeftijd plus duidelijke einde-trainingcheck.',validation='LiveContract test_04 + pausedWorkerProducesHonestBacklogMetric; businesscommit/outbox precies één, backlogstatus gecontroleerd.',communication='“Ontvangst werkt; verwerking ZEE wacht. Geen bewezen dataverlies. We herstellen de verwerking en controleren iedere open sleutel. Volgende update 09:30.”',lesson='Proceshealth is geen ketenhealth. Maak open trainingcontrols zichtbaar bij overdracht.',reproduce='request ADMIN PATCH /api/admin/controls {"worker_paused":true}; submit event; inspect journal; set false'),
dict(id='INC-002',slug='api-500-schema',title='API geeft HTTP 500 na ongeldige schemawijziging',severity='SEV2',impact='Voertuiglijst niet beschikbaar in test; productieachtige beslissingen uitsluitend geautoriseerd.',systems='Router, JDBC, schema',symptoms='500 INTERNAL_ERROR met correlation; SQLdetails niet naar gebruiker gelekt.',hypotheses='H1 tabel/schema ontbreekt; H2 authfout; H3 netwerk. 500 ná auth en requestlog weerspreekt 401/netwerk als eerste grens.',investigation='Runtime/config/artefact en schema_version vergelijken. Gereproduceerd in verse unit DB door vehicles te verwijderen, nooit in actieve main lab. Query faalt, router logt exception_class maar geen raw SQL/secret.',logs='request.internal_error, exception_class=IllegalStateException; request.completed 500. Root DB-exception alleen via bevoegde technische debug in test.',queries='Schema_version/information_schema via DBA; gewone query inventory. Geen CREATE/restore onder live users zonder herstelbesluit.',root='Scenario: foutieve migrationtarget verwijderd tabel die app verwachtte; codeversie en databasestate niet compatibel.',workaround='Stop releaseprogress, registreer current state en schakel veilige vorige testtarget in als bewezen compatible.',fix='Fresh-target restore of reviewed forward migration; predeploy schema gate en regression op ontbrekende dependency.',validation='routerInternalErrorSuppressesSqlDetails + WAR schema/query acceptance; geen ongefundeerde app-only rollback.',communication='“Testrelease heeft schema-afhankelijkheidsfout. We houden livegang tegen. Data-/schemastatus wordt eerst vastgesteld; daarna bevoegd herstelbesluit.”',lesson='500 is symptoom; eerste oorzaak ligt in deploy/schema, niet automatisch appcode.',reproduce='JUnit routerInternalErrorSuppressesSqlDetails uses isolated memory DB only'),
dict(id='INC-003',slug='slow-query',title='Langzame diagnosequery / indexpad controleren',severity='SEV3',impact='Tweede lijn vindt relevante errors te traag bij grotere volumes; timing in verhaal is geen gemeten benchmark.',systems='Journal query, index, report/diagnostic workload',symptoms='Filtering op status/error vraagt onderzoek van plan en rijen; geen fictieve voor/na-latencycijfers.',hypotheses='H1 onbegrensde scan; H2 lockwait; H3 volume/parameters; H4 runtimepool. Gebruik plan/locks/timing om te onderscheiden.',investigation='Run EXPLAIN via allowlisted slow-query-plan, noteer queryparameters en volume. Existing ready-index helpt queuequery; CHG-002 adds separate errorlookup index for diagnosis, not arbitrary optimizer tuning.',logs='request.completed timing context; SQLstate bij timeout; actual EXPLAIN output saved separately when executed.',queries='slow-query-plan; diagnostic failed-messages bounded 200; V002 errorindex idempotent. H2 plan is geen Oracle executionplan.',root='Scenario: errorlookup niet specifiek ondersteund en performance-eis niet gemeten; oorzaak/verbetering moet op representatieve dataset bevestigd worden.',workaround='Filter op bekende receipt/site/tijd en gebruik bounded queries; export niet de hele dataset tijdens incident.',fix='Reviewed additive index via CHG-002, DBA Oracle-portreview, measurement before and after under same workload.',validation='HTTP test_07 executes actual EXPLAIN; migration/recovery test confirms schema2; no speedup claim without measured baseline.',communication='“We begrenzen diagnosequery en beoordelen plan/volume. Er is nog geen bewijs voor algemene platformuitputting. Productie-DBA bepaalt eventuele indexchange.”',lesson='Index is geen magische fix; keyselectivity/locks/parameter scope eerst.',reproduce='request ADMIN GET /api/admin/diagnostics/slow-query-plan'),
dict(id='INC-004',slug='deployment-auth-config',title='Deployment start niet met verkeerde credentialconfig',severity='SEV2',impact='Testomgeving niet gereed voor release; geen users trainen op niet-valide target.',systems='Application init, WAR/container, secrets/config',symptoms='Application refuses missing/short/reused token; container deployment failure or local startup failure.',hypotheses='H1 ontbrekende envsecret; H2 incompatible Servlet/runtime; H3 DB filelock. Eerst init-exceptionclass en configkeys zonder values.',investigation='Artefact hash en containerlog; checklist required env keys; confirm separate runtime dir and correct credentials owner. Do not print env content. Validate constructor rejects invalid token configuration.',logs='Servlet init/config failure names required key but not token; deployment failed marker / containerlog.',queries='Geen DB-query noodzakelijk bij auth-initialisatie vóór DB-open; filelock alleen onderzoeken als init verder komt.',root='Scenario: releaseconfig miste één service token; configuration acceptance niet in deploycheck.',workaround='Go-live stoppen; eerdere compatible target houden; correctie alleen via credentialowner.',fix='Provide generated distinct credentials securely, redeploy correct environment, config preflight and negative startup test.',validation='configurationRequiresDistinctStrongSecrets; actual WAR health and positive/negative auth HTTP acceptance.',communication='“Het WAR is gebouwd, maar testconfig is niet compleet. Geen livegang. Credentials worden via eigenaar aangevuld, zonder ze in ticket of logs te delen.”',lesson='Build success bewijst geen environment readiness; secrets/config horen in releasemanifest boundary.',reproduce='Auth constructor test, not replacing main-lab credentials'),
dict(id='INC-005',slug='mapping-fails',title='Nieuwe partnerlocatiecode wordt afgewezen',severity='SEV2',impact='Afgebakende ALPHA-codevariant; andere geldige locaties blijven verwerken.',systems='Mapping, masterdata, journal, worker',symptoms='REJECTED / UNKNOWN_LOCATION for ZEE-A-01; receipt exists, no vehicle mutation.',hypotheses='H1 agreed alias missing; H2 genuine invalid location; H3 wrong site. Vraag businesscatalog/partnercontractbewijs.',investigation='Compare exact input code with active site masterdata and mapping version. v1 exact check rejects. v2 normalises only reviewed prefix then revalidates. No fictitious fallback location.',logs='message.rejected error_code UNKNOWN_LOCATION; controls/redrive audit records change and owner.',queries='failed-messages; check locations site/active; reconciliation empty before/after.',root='Scenario: approved partner alias absent in v1; contractchange was not coordinated with mappingdelivery.',workaround='Reject expliciet houden, partner originele agreed code laten sturen indien toegestaan; geen silent statusforce.',fix='CHG-003 mapping2 + site-negative tests + admin reasoned redrive of affected unprocessed IDs only.',validation='mappingFixAndAuthorizedRedriveAreAudited + HTTP03; processed redrive returns409; exactly one event/outbox.',communication='“Alleen codevariant ZEE-A-01 wordt geweigerd; bericht is bewaard. Partner/operations bevestigen de code, daarna beperkte mappingchange en gecontroleerde herverwerking.”',lesson='Mappingrelease is contractchange; both sites and invalid codes test.',reproduce='edi/samples/unknown-location.json; mapping2; redrive receipt'),
dict(id='INC-006',slug='ack-timeout',title='Partner-ACK faalt na geslaagde businesscommit',severity='SEV2',impact='Partner mist confirmation; intern voertuig correct. Retry business would be risky without dedup.',systems='Outbox, dispatcher, local callback',symptoms='Message PROCESSED, outbox RETRY_WAIT, ACK_TIMEOUT_OR_UNAVAILABLE; partner may send duplicate.',hypotheses='H1 callbacktimeout/unavailable; H2 commit missing; H3 HMAC rejected. Outboxstatus/commit distinguish.',investigation='Compare journal/business_event/outbox and callbackjournal on ack_id. Loss simulated with ack_timeout; actual HTTP call/HMAC also exercised. Repair acknowledgement only.',logs='message.committed before ack.failed; then ack.sent after recovery; same correlation/message ID.',queries='outbox-status + reconciliation; unique business_events/message relation.',root='Scenario: response path/callback unavailable after commit; sender confused receipt and outcome. No businessrollback.',workaround='Tell partner commit confirmed; maintain bounded ACK queue; no re-import to generate confirmation.',fix='CHG-001 independent ACK retries/outbox, idempotent signed receiver, bounded delays and alert. Restore callback safely.',validation='lostAckDoesNotReplayBusinessMutation plus HTTP/partner receipt; event remains one and ACK SENT.',communication='“Uw event is intern verwerkt; bevestiging wacht door callbackstoring. We herstellen uitsluitend de confirmationstroom. De eventkey blijft gelijk bij eventuele retry.”',lesson='Network exactly-once is not promised; durable outbox plus receiver dedup protects effect.',reproduce='ack_timeout true; smoke receipt; outbox-status; false; wait retry'),
dict(id='INC-007',slug='duplicate-deliveries',title='Dubbele verzending wordt voor dubbele voertuigen aangezien',severity='SEV3',impact='Business telt dubbele input; data-integriteit moet bewezen worden voordat correctie plaatsvindt.',systems='API/journal/deliveries/report',symptoms='Two transport receipts but one business event; repetition may use new message_id.',hypotheses='H1 same key same payload (safe); H2 changed payload same key (409); H3 new key actual event; H4 wrong report join.',investigation='Compare partner/event_key, canonicalhash and deliveryjournal, count business_events and current vehicles rather than transport attempts. Concurrent test sends16 requests and creates one effect.',logs='message.duplicate distinct request correlations, same system message ID.',queries='duplicate-records empty; count deliveries/message and events separately; occupancy.sql counts vehicles.',root='Scenario: transportattempts interpreted as businessobjects; duplicate prevention works, reporting definition was wrong.',workaround='Do not delete records; publish correct definition and reconcile by businesskey.',fix='PRB-003 / BR07 / regression report. UNIQUE partner/eventkey plus changed-payload conflict already implemented.',validation='concurrentDuplicateRequestsRemainUnique, reportCountsVehiclesNotDeliveriesAndHandlesBothSites, reportJoinAntiPatternIsDetected.',communication='“Er zijn twee afleverpogingen van hetzelfde event, één verwerking en één voertuig. We tonen sleutelbewijs; we verwijderen geen audit-/deliveryrecords om een telling te laten passen.”',lesson='Dedupbusiness and operationalreport meanings must both be explicit.',reproduce='Send arrival/duplicate fixtures; inspect deliveries vs occupancy'),
dict(id='INC-008',slug='token-rejected',title='Service account-token geweigerd / scope mismatch',severity='SEV3',impact='Een partnerstroom of gebruiker geblokkeerd; scope niet breed uitrollen.',systems='Auth/router, partner/client config',symptoms='401 for invalid bearer, 403 for role/site spoof, detail404 outside scope.',hypotheses='H1 bad/old token; H2 wrong role; H3 wrong target/site; distinguish401/403 without leaking secrets.',investigation='Identify accountrole/configowner, exact route/time, expectedscope and recent credentialchange. Compare working scoped request. No token values in incident or stdout.',logs='request.completed 401/403/404 with correlation; no Authorization header logged.',queries='No UPDATE account table; lab identity in env config. Site/partner data read by permitted owner only.',root='Scenario: BETA token used for ALPHA/ZEE request; rolemodel correctly denies.',workaround='Use correct authorized service identity through owner, not admin key in partner client.',fix='Clientconfig correction and role/scope negative tests; secretrotation should update owners/callback independently.',validation='partnerCannotSpoofScope, router auth test, HTTP02; tokens remain private and no data exposure.',communication='“De aanvraag past niet bij de gebruikte identiteit/scope. Wij verifiëren accountconfig met de eigenaar; geef geen token mee in e-mail.”',lesson='A forbidden request is not automatically an application outage.',reproduce='HTTP acceptance scoped token tests; no real token fixture committed'),
dict(id='INC-009',slug='report-inconsistent',title='Rapportcijfers wijken af door eventjoin',severity='SEV3',impact='Weekrapport kan verkeerde operationele indruk geven; bron/definitie afstemmen.',systems='Reporting SQL, deliveries/events, CSV',symptoms='Join count grows with retries/transitions while current vehicle inventory unchanged.',hypotheses='H1 one-to-many join; H2 different time/scope; H3 stale snapshot; H4 missing source records.',investigation='Same snapshot and businessobject. Compare vehicle keys, grouped report and illustrative bad join. Events/deliveries represent history, not current stock. Explain difference with one vehicle/two deliveries.',logs='Report request correlation/params; no fake refreshplatform. Data evidence from actual queries in test.',queries='occupancy.sql versus anti-pattern-delivery-count.sql (never production report); reconciliation keyset.',root='Scenario: event/deliverygrain used for vehiclecount; lack of accepted reportdatacontract.',workaround='Withdraw ambiguous report and show correct scoped vehicle count with explicit definition.',fix='PRB-003 reporting grain/definition, test cases null/multiple deliveries/two sites, signed businessacceptance simulated.',validation='reportJoinAntiPatternIsDetected + reportCountsVehiclesNotDeliveriesAndHandlesBothSites; CSV same aggregate.',communication='“Afwijking betreft teldefinitie, niet aangetoond voertuigverlies. We vergelijken dezelfde scope en leveren gecorrigeerd rapport met sleutelverklaring.”',lesson='DISTINCT toevoegen zonder begrip kan echte fouten verbergen.',reproduce='JUnit bad-join test + occupancy CSV endpoint'),
dict(id='INC-010',slug='application-unavailable',title='Applicatiepad unavailable met gecontroleerde recovery',severity='SEV2',impact='Portal/API-taken tijdelijk geblokkeerd; queue/data blijven durable.',systems='API readiness, portal, control/audit',symptoms='503 health DEGRADED and API failure under explicit lab control; admin controls recovery remains reachable.',hypotheses='H1 intentional faultflag; H2 DB unreachable; H3 container down; H4 route failure. If no HTTP connection, control path cannot fix runtime.',investigation='Check healthresponse versus connectionrefused; app/servletprocess and currentcontrolaudit; confirm timestamps/siteimpact. Lab force_api_failure proves503 handling, not physical networkoutage.',logs='request.completed503; controls LAB_CONTROL old/new; runtime/container log for genuinely absent process.',queries='Read-only diagnostics after recovery, reconciliation and outbox-state; never delete inputqueue.',root='Scenario: faultflag enabled for readiness rehearsal; handover did not state current availabilitymode.',workaround='Businessowner stops affected demo tasks; preserve state and updates. Real runtimeabsence escalate to platformowner.',fix='Admin clears explicit lab flag, health/true business smoke/reconciliation; improve critical-event/end-trainingcheck.',validation='HTTP06 + smoke both sites; no empty greencheck without businessflow.',communication='“Applicatiepad is tijdelijk niet beschikbaar. Data blijft bewaard; we herstellen de gecontroleerde toestand en testen daarna beide sites end-to-end.”',lesson='Know when recovery is app config versus OS/container; do not blanket restart.',reproduce='force_api_failure true; health503; admin reset; business-smoke')
]
for i,x in enumerate(incidents):
    day=f'2026-09-{14+i:02d}';timeline=f'{day} 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.'
    body=f"# {x['id']} — {x['title']}\n\n**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** {x['severity']}; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** {timeline}\n\n"
    for title,key in [('Business impact','impact'),('Affected systems','systems'),('Symptoms','symptoms'),('Hypotheses / counterevidence','hypotheses'),('Investigation','investigation'),('Logs','logs'),('Database checks','queries'),('Root cause in this scenario','root'),('Workaround','workaround'),('Permanent fix','fix'),('Validation / evidence boundary','validation'),('Communication','communication'),('Lessons learned','lesson'),('Lab reproduction','reproduce')]:body+=f'## {title}\n\n{x[key]}\n\n'
    write(f"docs/incidents/{x['id']}-{x['slug']}.md",body)
write('operations/incidents/index.json',json.dumps([dict(id=x['id'],title=x['title'],severity=x['severity'],status='RESOLVED_SCENARIO',document=f"docs/incidents/{x['id']}-{x['slug']}.md",simulation=True) for x in incidents],ensure_ascii=False,indent=2),False)

problems=[('PRB-001','repeated-ack-timeouts','ACK-fouten keren terug; retries blokkeren bij één thread mogelijk nieuwe businessverwerking.','Partner ziet onzeker resultaat en kan redundante input sturen; backlog en verkeerde herstelactie riskeren.','Callback/path tijdelijk unavailable → ACKsend fails → confirmationretry nodig → business/outbound waren onvoldoende onderscheiden → health/contract gaf geen expliciet effectbewijs.','Ontbrekend commit/ACK-datacontract en shared scheduling vergroten onduidelijkheid; no exactly-once-network delivery.','Durable outbox, independent processing/ACK scheduler, stable ack_id receiverdedup, bounded retries + alert; CHG-001.','INC-006/INC-010; JUnit response-loss + live outbox evidence; callbackfirstfailure vs dataeffects afzonderlijk.'),('PRB-002','recurring-location-mapping','Nieuwe locatiecodevarianten veroorzaken herhaalde rejects.','Afgebakende partner/siteflow vertraagd, handmatig “fixen” kan fysieke locatie vervalsen.','Codevariant niet bekend → master/mappingreject → contractsample niet afgestemd → versiechange niet als releaseafhankelijkheid → geen gezamenlijke owner voor codecatalog.','Vendorcontract ontbrekende voorbeelden en sitevarianten; verkeerde fallback zou probleem verbergen.','CHG-003 reviewed aliases, masterdatarevalidation, bothsite-negative tests, reasoned redrive and vendorhandshake.','INC-005; actual mapping/redrive tests; audit + one effect; reject validunknowncodes remains enforced.'),('PRB-003','reporting-grain-and-duplicates','Herhaalde meldingen “dubbele data” door telling van afleverpogingen of historyevents.','Onbetrouwbare operationele rapportinterpretatie; onnodige risicocorrecties en stakeholderwantrouwen.','Totaal verschillend → one-to-many join → verkeerde grain gekozen → rapportbusinessobject niet geaccepteerd → syntax/test alleen happy sample zonder duplicates.','Eventtijd versus verwerkingstijd, scope en refresh kunnen extra verschillen veroorzaken; eerst dezelfde snapshot.','BR07 vehiclegrain, canonical occupancyquery/CSV, duplicate/multisite regression and businessdefinition signoff.','INC-007/INC-009; anti-pattern test proves two deliveries versus one vehicle; no delete/DISTINCT workaround.')]
for id,slug,statement,impact,whys,factors,action,evidence in problems:write(f'docs/problems/{id}-{slug}.md',f'''# {id} — {statement}

## Problem statement / business impact
{impact}

## Timeline
Fictieve cyclus: eerste incident week1 → herhaling week2 → RCA week3 → approved workpackage week4 → regression/nazorg week5. Exacte corporate historie niet geclaimd.

## Root cause analysis / 5 Whys
{whys}

## Contributing factors
{factors}

## Permanent corrective action
{action} Simulated owners: officer coördineert; developer/integrationpartner levert testbaar werk; business accepteert definitie/gedrag; supervisor autoriseert change.

## Verification / prevention
{evidence} Open action owners en acceptance in release1.4.0. Preventie is pas afgesloten als herhaling met regressie/monitoring wordt gedetecteerd of voorkomen. Geen “menselijke fout” als eindoorzaak.
''')

changes=[('CHG-001','retry-and-replay','Onafhankelijke verwerking, durable outbox en begrensde retries','INC-006 / PRB-001; input en ACK mogen elkaar niet verkeerd herhalen.','Java Worker/Application scheduling, outbox, partnercallback en alert/runbook; geen userdatacontractremove.','Dubbele delivery, partial commit, verkeerde retry van permanent4xx; singleinstance blijft beperking.','Implement message/ACK separatie en 5-attempt1–16s delays; two independent scheduled tasks; receiver stable-ID/HMAC; logging aftercommit.','JUnit lost ACK/transient/deadletter/concurrency + live partner callback. Test permanent4xx and no businessrepeat.','Stop consumers within mandaat, preserve journal/outbox, revert compatible WAR if schema unchanged. Never re-import PROCESSED to forceACK.','Businessloop and callback receipt; reconciliation empty; attempts bounded; audit of any redrive.'),('CHG-002','database-index-optimization','Additieve errorlookup-index','INC-003; diagnosequery bij fouten moet een beoordeeld indexpad hebben.','V002 error index/schema_version2, diagnostics; geen table/data transformation.','DDL autocommit, filelock, workload-specific plan; geen gegarandeerde speedup.','Stop lab app; snapshot; copy reviewed V002 inside runtime; DbTool migrate; compare schema_version and EXPLAIN; restart/validate.','Fresh DB migration applied twice safely; capture actual plan; same dataset/time and query if measuring speed.','Index mag achterblijven bij approllback; only remove via reviewed follow-up. Restore snapshot to fresh target for genuine data recovery, not blind overwriting current DB.','Schema2 present, constraints/data unchanged, diagnostic query/smoke pass; actual performance claim only if measured.'),('CHG-003','update-integration-mapping','Gereviewde locatiealiases met gecontroleerde redrive','INC-005 / PRB-002; partnerformat agreed alias ontbreekt in mapping1.','Current mappingcontrol2; ZEE/KAL codevariant, inputjournal, rejected messages and audit.','Te brede normalisatie, wrongsite, verwerking van reeds gecommitteerd event of partnerreplay with altered payload.','Partner/keyuser bevestigen exact aliases; enable mapping2 by admin; test invalid/wrongsite; list rejected IDs; reasoned redrive only allowable statuses.','mappingFixAndAuthorizedRedriveAreAudited; HTTP03; siteconstraint, version/hold rules unchanged; negative unknownalias.','Set mapping1 again; leave historic processed records/audit intact. Back-out newly created businessdata is separate authorized correction, not automatic mappingrollback.','Affected IDs one event/outbox each, UNKNOWN_LOCATION only for truly invalid codes, partnerACK and scoped inventory checked.')]
for id,slug,title,trigger,impact,risk,implementation,test,rollback,verification in changes:write(f'docs/changes/{id}-{slug}.md',f'''# {id} — {title}

## Aanleiding / impact
{trigger} {impact}

## Scope / risico
{risk} In scope bovenstaande componenten; out of scope echte ICO-app/Oracle/AIX. Stopcriteria: unexplained data diff, authorization gap, missing recovery or critical UAT failure.

## Implementation plan / work packages
{implementation} Owner: lab developer/integration role; officer coördineert acceptance en dependencies.

## Test plan
{test} Include happy, negative, concurrency and recovery; attach actual output, not checkbox only.

## Rollback / recovery
{rollback}

## Approval / deployment window
Simulated request to IT Supervisor + businessowner; approval record status **PROPOSED / lab rehearsal**, not real approval. Illustrative window 2026-09-28 16:00–17:00 UTC, conditional on stable operations and available vendor/data/runtimeowners. Budget/capacity in projectforecast. No actual message sent.

## Verification / closure
{verification} Releaseowner records hash/config/schema/mapping, known issues and nazorgowner. Businessacceptance and technical validation separate.
''')

runbooks=[('api-failure','401/403/409/429/5xx or transport failure','Failed user/partner task, determine site/partner and physical deadline','health and actual route/status/correlation; compare one known-good request','health; request ADMIN GET /api/messages; log-summary','request.completed, request.internal_error; never tokens','Bad auth/scope, wrong contract, quota, controlled dependency failure or DB exception','Fix first proved boundary with owner; same eventkey retries only for transient transport/5xx; do not bypass auth','Service Desk → officer → runtime/data/integration owner; security if exposure','Contract negative tests, rate/timeout agreement and business-smoke'),('database-issue','SQL error/lockwait, missing records or DB readiness failure','Data integrity and all DB-dependent flows','Schema version, correct target/filelock, recent migration; no direct DML','reconcile; request ADMIN GET /api/admin/diagnostics/recent-errors; offline schema query only with owner','database.error SQLstate; deployment/schema history','Wrong schema, locked file, resource issue or incompatible migration','Use approved recovery path; snapshot/restore fresh target after stopping app; audit data differences','DB/runtimeowner; do not kill arbitrary session/process','Migration gate, actual backup/restore rehearsal, bound queries'),('integration-failure','RETRY_WAIT/DEAD_LETTER, partner missing result','Partner/site flow and backlog urgency','Receipt status, last good step, contract/mapping and callbackjournal','failed; request ADMIN GET /api/admin/diagnostics/outbox-status; reconcile','received → retry/rejected/committed → ack.failed/sent','Unavailable dependency, unknowncode, version/order/hold or ACKfailure','Repair cause, wait bounded retry; admin reasoned redrive only uncommitted failure; ACK only if businesscommitted','Integrationpartner plus businessowner for semantics','Idempotence, contractfixtures, oldest-age/deadletter alerts'),('authentication-issue','401 invalid token,403 scope/role,404 invisible detail','One account/task vs global outage','Identity/route/scope/configowner; no secrets in evidence','request READER GET /api/vehicles; use correct role, inspect status only','request.completed with correlation/status','Wrong/old token, role mismatch, partner/site or targetwrong','Credentialowner repairs config; minimum role only; regression denied requests','Identity/securityowner if suspected leak; supervisor mandate','Separate roles/owners, startup configvalidation, secure rotation'),('application-unavailable','Connection refused,health503,portal task fail','Scope site/critical task; preserve physicaltraceability','Process/container first vs API readiness; latest deployment and controls','health; smoke after recovery; inspect owned app/container log','application.started / servletdeployment markers / request503','Appdown, config/DB-initfailure, force_api_failure or network','Authorized service/config restore; health plus real businesscheck; no blanket restarts','Runtimeowner for process/OS, officer for chain, operations for workaround','Rehearsed deployment/availability checks; not health alone'),('deployment-failure','WAR failedmarker,wrong version/schema,postdeploy task failure','Hold go-live; avoid mixedversion effects','Manifest/hash, target config,secrets keys,schema,current marker; stop unplanned changes','release-manifest; health; actual server-log; signed window checklist','WildFly .failed/server.log, initexception withoutsecret','Wrong artifact/env,initcredential,DBfilelock or incompatible schema','Inventory state; safe compatible WAR revert or fresh data recovery/forwardfix; go/no-goowner','Releaseowner+runtime/data+vendor, supervisor decision','Preflight/config/UAT and restore rehearsal'),('slow-performance','Slow request/query/backlog without clear error','Which task/volume/deadline, not generic servercomplaint','Baseline/params/rows, timing boundary,locks and inputburst','request ADMIN GET /api/admin/diagnostics/slow-query-plan; alerts; record before/after sameworkload','Mean request metric is cumulative; do not inventp95; eventtime/queueage','Expensive query,waiting lock,callback head-of-line,too muchinput','Bound scope, fix measured cause, reviewed index/scheduler change; no blind tuning','DBA/runtime/integration capacityowner as evidence indicates','Representative loadbaseline, accepted target and alert'),('malformed-message','400 syntax/validation or async UNKNOWN_LOCATION','Only affected samples; transport !=businesssuccess','Shape/types/date/mandatory/extra; businesscode contract and site','Submit edi/samples through partner; failed and journal read','MALFORMED_JSON,VALIDATION_ERROR or message.rejected','Bad syntax/type/futuretime/unknownfield or code/catalogwrong','Sender corrects contract; samekey changedpayload409 must explicit ownerdecision; mapping via CHG003','Partnercontractowner/businessmasterdata','Strict validation, samples and negative tests'),('missing-data','Physical action exists but record/report absent','Locate vehicle/task and safe operationalstate','Same key,time,site/source; receipt vs commit vs reportdefinition','journal; failed; reconcile; occupancyreport','received/rejected/retry, processed and reportquery context','Unprocessed input,wrongscope,statusdefinition, eventorder or join/filter','Fix first failed boundary; no fabricated record to fixcounts; businessownerconfirmsphysicalstate','Operations/data/integration; security if scopeexposure','Keyset reconciliation, freshness/businesshealth and sourceoftruth'),('duplicated-data','More delivery/event rows than expected objects','Determine duplicateeffect vs harmless repeateddelivery','Business key/hash,transport IDs,vehicle/event/outbox counts','duplicate-records; reconciliation; occupancyquery; anti-pattern only in test','message.duplicate same receipt; conflict changedpayload','Expected retries,changedkeys,reportgrainwrong or genuine race','Unique/atomic enforcement; do not deleteaudit/delivery; correct proved dataissue by authorized plan','Data/integrationowner; businessdefinitionowner for report','Concurrent/timeout tests,contractkey agreement and reportnegativefixtures')]
for slug,symptom,impact,firstchecks,commands,logs,causes,resolution,escalation,prevention in runbooks:
    write(f'docs/runbooks/{slug}.md',f'''# Runbook — {slug}

## Symptoms
{symptom}
## Impact
{impact}. Prioriteit volgt impact/urgentie/veiligheid; simulatie-SEV is geen ICO-SLA.
## First checks
{firstchecks}. Schrijf tijd/zone/owner en laatste goede grens op; één onderscheidende test per keer.
## Commands / queries
`python3 src/scripts/manage.py` gevolgd door: {commands}. Default is lokaal en read-only; smoke maakt expliciet synthetische events. SQLrefs in database/diagnostics. Geen productiecommando zonder versie/runbook/mandaat.
## Logs
{logs}. Redigeer gevoelige data; bewaar originele correlation evidence volgens retentie.
## Likely causes
{causes}. Hypothese pas oorzaak noemen met bewijs/weerlegging.
## Resolution
{resolution}. Gebruik changeprocedure en recoveryplan; functioneel/business/data/ACK opnieuw controleren.
## Escalation
{escalation}. Stuur impact,tijdlijn,ID,laatste goede grens,uitgevoerde tests en benodigd besluit; geen onbewezen ETA.
## Prevention
{prevention}. Koppel terugkerende fouten aan problem,regressie/alert/contract en eigenaar/einddatum.
''')
write('docs/runbooks/on-call-handover.md','''
# Wachtdienst / tweede-lijnsoverdracht

Vacature bevestigt wachtdienst, rooster/vergoeding/responstijd onbekend. Simulatie checklist: toegang test/production duidelijk; incidentowner en backup; huidige release/hash/config/schema/mapping; open incidents/workarounds en oudste backlog; laatste goede commit/ACK; vendor/data/runtime/securitycontacts en besluitmandaat; komende changes; keys/path veilig beschikbaar zonder ze in ticket te plakken.

Voor oproep: task/site/partner/time/ID, fysieke impact/urgentie en wat Service Desk al gecontroleerd heeft. Eerste vijf minuten: veiligheid/scope, owner, last healthy boundary, recente changes, sample, volgende update. Escaleer zonder productierechten/kennis of bij data/security/veiligheidsrisico. Geen zelfstandig rootbeheer, global restart of SQLcorrectie omdat klok tikt.

Overdrachtrecord: known/unknown/action/owner/nextupdate; tijdelijke workaround met einddatum en reconciliatie. Eindshift: controls terug naar intended state, backlog/ACK/reconciliation gecontroleerd, actionowners confirmed. Nieuwe medewerker pas wachtdienst na lokaal afgesproken readiness en shadowing, niet kalenderdatum alleen.
''')

write('docs/releases/REL-1.4.0.md','''
# Release 1.4.0 — Terminal Flow Control

## Features / fixes
Durable partnerreceipt, strict scope/idempotency; atomic state/event/audit/outbox; independent processing/ACK scheduler; bounded retry/reasoned redrive; operator correction and businesshold control; both-site SQL/CSV reports and registered diagnostics; portal and local operations CLI. Fixes simulated problems PRB001/002/003 through CHG001/002/003.

## Database / integration changes
Schema1 transactional objects, optional reviewed additive V002 errorlookup-index/schema2. Mapping1 exactcodes, mapping2 reviewedaliases with masterdatarevalidation. Partnercontract unchanged mandatoryfields; ACK is separately signed/persisted and idempotent.

## Deployment order
Confirm synthetic testscope / config / backup; build/tests/hash manifest; stop old lab instance; snapshot and compatible schemachange if approved; configure separate target and correct secrets; deploy WAR; wait actual deploymentmarker; health/auth/business UAT; bothsites, ACK, datareconciliation; training/handover/nazorg. Every step assigned in checklist. Buildgreen is not go-liveauthorization.

## Go/no-go and simulated approval
Only PROPOSED/LAB REHEARSAL approval. Required: actual automated tests pass, current schema/mapping/artefact known, critical UAT/security/safety gates satisfied, rollback/recovery feasible and business/vendordekking. No-go on unexplained diff, unauthorized correction, missing critical task or unknown recovery. Known productgaps accepted explicitly; no claim of approved ICO release.

## Known issues / limitations
Singleinstance; H2 not Oracle; no real AIX/iWay/WebFOCUS/APEX. HTTP/role tokens only localhost. Lists bounded 200, no full UIpagination. Retry timing lab1–16s, no production SLA/jitter. Current report rather than historical shipmentanalytics. No true businessintegrationevent emitted for portal correction: audit/vehicle state updated; downstream notification needs separate contract/change before production. Callback allowlist loopback only.

## Rollback strategy
Compatible code/config/mapping back-out preserves history; processed input never replayed to “restore”. Additive errorindex can stay. Data restore only into fresh target from verified snapshot, then compare post-snapshot/in-flight events and decide replay safely. Back-out mapping2 does not undo already processedvehicles. App-only rollback cannot assume database/data compatibility.

## Smoke tests / release notes
health200, invalid token401, partner scopes, newevent202→PROCESSED for ZEE/KAL, duplicate200 sameeffect, callback HMACreceipt/SENT, operator version/reason/audit, readerwrite403, CSVaggregate correct, reconciliationempty. Commands/tests in verification.md. Users: correctionreason/version required; receipt !=commit; report grain=unique currentvehicle. Support: runbook links, bounded retry and no blanket re-drive.
''')
write('deployment/release-checklist.md','''
# Release checklist

- [ ] CRQ/businessscope and simulated approval/real mandaat stated.
- [ ] App/schema/mapping/partnercontract versions and target known.
- [ ] Tests/UAT/negative authorization and safety criteria pass.
- [ ] Actual WAR SHA256 compared; secrets external, correct environment.
- [ ] Current instance stopped for file maintenance; backup integrity confirmed.
- [ ] DB/mapping order and recovery/forwardfix explicitly assessed.
- [ ] Vendor/keyuser/runtime/data/Service Desk available and informed.
- [ ] Deploy marker shows success, no first exception hidden.
- [ ] Technical health plus two-site business smoke and signed ACK pass.
- [ ] Reconciliation/report definitions/remaining backlog checked.
- [ ] Usertraining, release notes and on-call handover available.
- [ ] Nazorgowner/time and open problems/actions agreed.

Attach evidence; never simulate an actual approval signature. Lab checklist does not grant ICO production rights.
''')
write('deployment/deployment-runbook.md','''
# Deployment runbook

Developer → review/CRQ → Maven build/tests → WAR/hash → testtarget/config → UAT/recovery → approved window → deploy → end-to-end validation → nazorg. WAR bundles webapp classes/resources/dependencies; EAR can bundle multiple enterprise modules, but none needed here. Servlet container is application server; exact ICO JBoss variant unknown.

## Fast local development
`mvn -B -ntp package`, `python3 src/scripts/manage.py init`, `start`, `smoke`. Stop via owned-process `stop`, not global pkill. Local adapter is JDK HttpServer, not fake JBoss. Correct directory/env/ports required. Secrets runtimeonly; portal token manually retrieved locally by owner, never committed.

## Genuine WAR lab
`python3 deployment/scripts/wildfly_lab.py install` downloads official pinned EE10 release and validates SHA256. `start` uses separate DB under runtime/wildfly and loopback HTTP+management ports; deploys actual terminal-flow.war via standalone scanner, confirms .deployed/.failed. `test` runs same HTTP acceptance contract under /terminal-flow. `redeploy` undeploys/loads WAR and checks resource/lifecycle persistence; `stop` uses owned process identity. No Docker dependency; server binary/runtime ignored by Git.

Production deployment method must be confirmed with true runtimeowner; scanner is local simulation, not guaranteed preferred enterprise release method. Environment configuration includes app-role secrets, DB target, callback/HMAC, port and limits. No secretliteral in WAR. Logs: runtime/app.log or server.log plus journal/query/audit; inspect first failure not just final “server started”.

Migration: stop target; reviewed snapshot; DbTool migrate file copied inside runtime; DDL may auto-commit. Never assume data rollback. Validation includes real task/input/commit/callback, not health alone. Stop/no-go on unknown state, data/security/safety defects or absent recoveryowner.
''')
write('deployment/rollback-plan.md','''
# Rollback / recovery plan

Trigger: critical acceptance failure, schema/data inconsistency, wrongscope, unsafe transition or unknown state. Releaseowner freezes further changes, inventories completedsteps and current app/config/schema/mapping/data. Businessowner determines temporary physical workflow. Supervisor/runtime/dataowners decide compatible back-out vs forwardfix vs fresh restore.

App/WAR back-out only when previous code compatible with current schema/data. Controls/mapping rollback audited; history stays. V002 index is additive and can remain. A processed partner event cannot redrive; removing outbox or altering journal to regenerate state is forbidden. Different transport IDs with same key already idempotent.

Offline recovery lab: stop app → DbTool backup into new runtime snapshot → record SHA256 → restore only to **fresh** file database → reopen/reconcile/compare snapshot keys → deploy compatible WAR/controls → business+ACK checks → handle events after snapshot through explicit ledger. Original database never overwritten automatically. Snapshot truncation or schema mismatch is no-go. No claimed zero-data-loss outside checked snapshot/in-flight boundary.

Actual Oracle/enterprise backup, RPO/RTO and restore ownership not simulated as productproof. Those require vendor/DBA procedures and real rehearsal. Workaround may be safe while permanentfix proceeds but has owner/limits/enddate/reconciliation.
''')
write('deployment/post-deployment-validation.md','''
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
''')
write('docs/releases/cutover-rehearsal.md','''
# New-terminal-system cutover rehearsal

Fictief oud/nieuw datamodel is dezelfde businesskey/statevariant, niet een genoemd ICO-product. Exercise: source snapshot → target migration result → key/field reconciliation → go/no-go → route/in-flight handling → businessvalidation. Cutover script checks snapshots, does not pretend to perform a real vendor migration.

`python3 deployment/scripts/cutover.py deployment/environments/source-snapshot.json deployment/environments/target-bad.json` must fail with missing/wrong key. Correct target passes. Compare VIN, partner/site,location,state,version; countonly is insufficient. Empty snapshots, duplicatekeys or unexpectedfields are rejected. Script output is concrete JSONdifference report and exitcode2 on mismatch.

Production-like steps: freeze/snapshot agreed with business; durable inventory of in-flight partner events and last processedkey; migrate history/status/masterdata; compare same cutoff; stopgo-live on unexplaineddiff; preserve oldroute until decision; switch partnerroute; apply delta with duplicate-safe keys; verify physical/business state and ACK; retain exit/recoverywindow. Restoring oldsnapshot can lose newerchanges, so no unsupported zero-loss claim.

This repository actually tests H2 backup/freshrestore and keydiffgate; it does not operate a real new ICO TOS. Open product/mapping/history/RPO/RTO questions remain on onboarding agenda.
''')

write('docs/stakeholders/raci.md','''
# Stakeholders / RACI — fictieve rolverdeling

R executes, A owns/decides, C consulted, I informed. Real ICO mandaat must be confirmed. Vacancy reports Supervisor/Director and contacts internal/external team,projectcoordinator,business,customers/vendors/Service Desk; separate runtime/data/security roles are assumptions.

| Activity | R | A | C / I |
|---|---|---|---|
| Incidenttriage/businessimpact | Service Desk/officer | Incidentowner | Keyuser/runtime/data/vendor; businessupdated |
| Permanent technicalfix | Developer/integrationpartner | IT supervisor | Officer/test/business |
| Physical hold/release rule | Businessoperations | Businessapprover | IT implements/audits, not autonomous release |
| Data/schema/recovery | Dataowner | Authorized IT/dataowner | Runtime/officer/business |
| Vendorworkpackage/acceptance | Officer | Supervisor/budgetowner | Projectcoordinator/keyuser/vendor |
| Release go/no-go | Releaseowner/officer | Supervisor + businessowner | Runtime/data/vendor/Service Desk |
| Reportdefinition | Businessdataowner | Businessunitowner | Officer/reportdeveloper |
| Securitycontainment | Security/runtimeowner | Securitylead | Officer/management; controlled externalcomms |

One incidentowner, one actionowner per follow-up, no responsibility without decisionrights. Externalupdates use approved channel; repo samples never actually sent.
''')
write('docs/stakeholders/vendor-work-package.md','''
# Vendor work package — WP3 integration delivery

Objective: preserve one business effect per eventkey and give accurate aftercommitACK. Deliver: contractprofile/samples, mapping1/2, error semantics, duplicate/concurrency/timeout tests, component/configversion, rollout/recovery instructions and supporthandover. In/outscope explicit; productlicense and actual vendor unknown.

Acceptance evidence: deterministic tests; sample badcode/recovery; transportidchange and payloadconflict; callbackresponse loss; HMAC invalid rejection; bothsites; firstfailurelog/correlation and safetyholds. Provider claiming “works here” without matching sample/version does not close issue. Officer independently validates chain/businessoutcome.

Actionlog (fictief): V-01 aliases verify / partnerowner / 2026-09-24; V-02 signedACKretry demo / integrationvendor / 09-25; V-03 recoverymanifest / runtimeowner / 09-26; V-04 UATtraining / keyuser+officer / 09-27. Escalate missed acceptance or10% forecastdrift with options: reduce scope, move window or add agreedcapacity. Contract/budgetapproval stays assignedowner.

Question to supplier: “For receipt X/eventkey Y at Z UTC, our journal proves commit; outbox shows callbacktimeout. Please provide matching receiverlog/ACK semantics and next testwindow. No credential in reply.” Outsourcing includes documentation/exitknowledge, not surrendering architectureownership.
''')
write('docs/stakeholders/weekly-report.md','''
# Weekly report — illustrative week ending 2026-09-25

To: ITdepartment + businessunits (sample, not sent).

**Resultaat:** vertical integration acceptance now covers duplicates,mappingrejects,holds and ACKloss; portal has currentversion/reason/audit; bothsite reports use uniquevehicledefinition. Actual executed testcounts/results live in verification.md; this narrative does not claim ICO delivery.

**Risico:** real productport (Oracle/AIX/iWay/WebFOCUS/APEX) remains untested; callbackcontract/identity/TLS enterprise choices unknown. Additiveindex effect requires measuredworkload, no invented speedup. Current lab singleinstance is deliberateboundary.

**Capaciteit/budget:** WP3/5 competing for same resource; fictiveforecast in capacity-budget.csv shows escalationthreshold. Definition of done=accepted output, not hours spent. Keep incidentbuffer; no silent unpaid overtimepromise.

**Besluit nodig:** approve lab mapping2acceptance and separate productdiscovery before enterpriseport. Options: freeze equivalentdemo scope (lowercost) or reserve actual vendor/sandboxvalidation (more time, strongerproductproof).

**Next:** officer updates differencegate/runbook; keyuser does teach-back; runtimeowner confirms WAR/recovery; each owner/date in actielog. Open recurringissue →problem, not closed with restartalone.
''')
write('docs/stakeholders/communications.md','''
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
''')
write('docs/stakeholders/multilingual-updates.md','''
# N / E / F — operational communication samples

Vacature zegt N/E/F; interpretatie Nederlands/Engels/Frans en gewenst niveau moeten bevestigd worden. Dit bewijst documentvoorbereiding, geen persoonlijke spreekvaardigheid.

**NL:** “Het bericht is ontvangen, maar nog niet verwerkt. We controleren de mapping en de huidige voertuigstatus. Gelieve dezelfde businessreferentie te behouden bij een retry. Volgende update om10:30UTC.”

**EN:** “The message was received but has not been processed. We are checking the mapping and the current vehicle state. Please keep the same business reference for any retry. Next update at10:30UTC.”

**FR:** « Le message a été reçu, mais il n’a pas encore été traité. Nous vérifions le mapping et l’état actuel du véhicule. Veuillez conserver la même référence métier lors d’une nouvelle tentative. Prochaine mise à jour à10h30UTC. »

Actionlog always owner/date/expectedoutput; confirm shared meaning of receipt/commit/ACK across languages. Recipient repeats expectedaction, not just “understood”.
''')
write('docs/onboarding/30-60-90-day-plan.md','''
# First 90 days simulation

## Days1–30 — systems understanding
Supervisor scopes mandaat/priority; ServiceDesk shows escalation/on-call; keyusers show arrival/location/departure and physicalholds for each site; component/data/vendorowners walk oneevent. Access leastprivilege,correct environments/secrets. Produce validated component/process/RACI map, one shadowed evidencepack, tenunknowns and buddyreview. Read-only reconcile and small docfix; no uncontrolled productionchanges. Watch/readiness only after explicit training.

## Days31–60 — independent operations
Handle bounded incidents with impact/hypotheses/validation and regularupdates. Draft CRQ/werkpakket, coordinate partnerfix in test, perform scope/negativeUAT, deliver one small tool/portalchange with review and teach-back. Weekly forecastacceptedwork and capacity/budgetrisk. Milestone: accepted change, complete incident closure, colleague can use runbook.

## Days61–90 — ownership and improvement
Agree ownership of one component/interface/projectworkpackage. Solve recurringissue via problem/change/regression/alert. Coordinate release/restore rehearsal; maintain product/version/lifecycleinventory. Report measured improvement and remainingrisks, no fictionalsuccessnumbers. Milestone: domainhandover, actualevidence release, forecast and 90-dayreview with supervisor; next responsibility not calendarautomatic.

Actual products/procedures/team/servicelevel remain unknown; adapt to ICO. Degree/benefits/travel/language/availability are onboarding/HRchecks, not engineering outputs. Repository cannot prove those qualifications.
''')
write('docs/onboarding/user-training.md','''
# User training / teach-back

Audience: fictiveoperationskeyuser. Task: find scopedvehicle,verifyphysicalposition,readcurrentversion,selectvalidsame-sitelocation,enterreason,correct,checknewversion and audit with authorizedowner. Wrongversion →reload,notrepeatblind; wrongsite →nochange; readercannotcorrect; hold release requires businessdecision/adminrole in lab.

Before: own labtoken via secureowner,syntheticdata,correcttarget/version,recordedexpectedresult. Instructor shows one case,participant performs new case and one exception. Participant explains receiptversuscommit and who handles unknownstatus. Trainingacceptance: unaidedtask,faultrecognition,escalationchannel and instructionfeedback. Documents version1.4.0 and owner/date; retiredscreens removed.

Employeeonboarding teach-back: follow oneALPHA event input→journal→commit→outbox→callback→report. Diagnose badalias or ACKtimeout with query/runbook without executing globalrestart. Clear intendedfaultcontrols and handover openactions aftersession.
''')
write('docs/onboarding/buddy-plan.md','''
# Buddy / new employee training

Day1 access/mandaat/safety/escalation and contacts; day2 keyuserphysicalprocess/site differences; day3 component/dataflow/versions and logs; day4 shadowincident/change and recovery; day5 new colleague explains chain and documents openquestions. Buddy reviews maps and prohibits unknownproductionactions.

Week2 co-investigate one real/testticket,write2hypotheses,evidence and businessupdate; week3 smallCRQ/UAT/training; week4 release/handover. Growth from knowing→understanding→withhelp→independent→expert per task. Newcolleague must state exact productlab/professionalexperience. No meritclaim based solely on readingmanual.

Checklist: reproducible task,errorpath,logs/queryowner,scopechecks,stable businesskey,commit/ACK distinction,stop/no-go and who decidesphysicalrelease. Buddy asks “what would disprove your hypothesis?” and “what could this recovery lose/duplicate?” before readiness.
''')

write('operations/portfolio/capacity-budget.csv','wp,planned_hours,actual_hours,remaining_hours,forecast_hours,rate_eur,forecast_eur,context\nWP1,12,12,0,12,80,960,SIMULATION\nWP2,18,16,4,20,80,1600,SIMULATION\nWP3,24,20,10,30,90,2700,SIMULATION\nWP4,18,12,6,18,80,1440,SIMULATION\nWP5,16,8,10,18,90,1620,SIMULATION\nWP6,8,2,6,8,70,560,SIMULATION',False)
write('operations/portfolio/project-portfolio.csv','project,priority,business_outcome,dependency,owner_role,status,context\nTFC-reliability,HIGH,One effect and visible ACK,Partner contract,Development officer,LAB_IMPLEMENTED,SIMULATION\nTerminal-cutover,HIGH,Consistent keyset migration,TOS product discovery,Project coordinator,REHEARSAL_ONLY,SIMULATION\nError-lookup,MEDIUM,Explainable bounded diagnosis,DBA workload measurement,Data owner,ADDITIVE_LAB_CHANGE,SIMULATION\nProduct-port,MEDIUM,Verify Oracle AIX iWay WebFOCUS APEX,Sandbox licensing and real versions,IT supervisor,PROPOSED,SIMULATION',False)
write('docs/role/automation-register.md','''
# Automation register

| Manual → automated | Working command | Benefit / safety |
|---|---|---|
| Repeated health/openroute check → healthCLI | manage.py health | Actual200/503, exit1 onfailed; read-only |
| Scrolljournals forfailedinputs → allowlisted SQLinventory | manage.py failed | Reject/retry/deadletter separated; read-only |
| Guessbacklogimpact → metricthresholdalerts | manage.py alerts | Owner/action, exit2 activealerts; no fakeSLA |
| Handcomparecommit/outbox → invariantquery | manage.py reconcile | Keyconsistency,exit2differences,notbulkcorrect |
| Repeated deploymentchecking → businesssmoke | manage.py smoke | Newsyntheticevents bothsites+duplicateproof; explicitmutation |
| Readlogmanually → JSONeventsummary | manage.py log-summary | No secret/rawpayload; countersnotrootcause |
| CopyunversionedWAR → hashmanifest | manage.py release-manifest | SHA/version/revisionproof,local file only |
| Countmigrationrows → cutoverkey/fieldgate | cutover.py source target | Exit2diffs prevents falsereadiness |

Do not automate destructivecorrection or businessrelease without decision/mandaat. Scripts have explicit target/role, bounded requests and documentedexitcodes. Production benefits require realbaseline, not illustrative time-savingpercentage.
''')

write('database/queries/anti-pattern-delivery-count.sql',"-- Demonstration only: wrong grain. NEVER use as operational vehicle report.\nSELECT v.site_id,COUNT(*) AS incorrect_vehicle_count FROM vehicles v JOIN messages m ON m.vin=v.vin JOIN deliveries d ON d.message_id=m.id GROUP BY v.site_id;",False)
snapshot=[dict(vin='DEMO0000000000001',site_id='ZEE',partner_id='ALPHA',location_id='ZEE-A01',state='ACTIVE',version=1),dict(vin='DEMO0000000000002',site_id='KAL',partner_id='ALPHA',location_id='KAL-B01',state='ACTIVE',version=1)]
for name,rows in [('source-snapshot',snapshot),('target-good',snapshot),('target-bad',[dict(snapshot[0],location_id='ZEE-A02')])]:write(f'deployment/environments/{name}.json',json.dumps(rows,indent=2),False)
write('deployment/environments/local.example.env','''# Names / non-secret defaults only. Real random credentials generated in runtime/.env.
ROLEOS_PORT=8090
ROLEOS_ACK_URL=http://127.0.0.1:8091/ack
ROLEOS_DB_URL=jdbc:h2:file:./runtime/terminal;MODE=Oracle;DB_CLOSE_DELAY=-1
ROLEOS_RATE_LIMIT=120
# Required random runtime values: ROLEOS_ALPHA_TOKEN, ROLEOS_BETA_TOKEN,
# ROLEOS_READER_TOKEN, ROLEOS_OPERATOR_TOKEN, ROLEOS_ADMIN_TOKEN, ROLEOS_ACK_SECRET.
''',False)

tickets=[
('INCIDENT','HIGH','Worker backlog ZEE','Partnerreceipt blijft RECEIVED; bevestig scope en last-good commit.','Arrival tasks uncertain; preserve physical traceability.','Resume authorized worker, one event/outbox per key and backlog tracked.','INC001 / live04 / oldest-age','RESOLVED_SCENARIO'),
('BUG','HIGH','Missing schema yields500','Testrelease vehiclequery faalt; geen SQLdetails extern.','Portal blocked, go-live no-go.','Fresh schema/recovery + HTTP500 sanitized test pass.','INC002 / isolated memory test','RESOLVED_SCENARIO'),
('INVESTIGATION','MEDIUM','Explain errorlookup performance','Meet query/parameters/volume en bekijk EXPLAIN.','Diagnose may slow at larger volume.','Record actual plan, baseline if speed measured; no invented gains.','INC003 / CHG002','IN_REVIEW_SCENARIO'),
('ACCESS','HIGH','Incomplete deploy credentials','Verify envkeypresence/minimumlength/distinct roles.','Deployment not ready for users.','Startup rejects badconfig; positive/negative auth succeeds after ownerfix.','INC004 / Auth validation','RESOLVED_SCENARIO'),
('CHANGE','HIGH','Mapping alias2','Agree exactaliases for bothsites and invalidcode cases.','Specific partnercode rejected.','V2 validaliases work, invalidsite denied, reasoned redrive once.','CHG003 / live03','LAB_IMPLEMENTED'),
('INCIDENT','HIGH','Missing callback ACK','Separate internalcommit from externalconfirmation.','Partner cannot trust outcome.','One effect, signedreceipt and SENT ACK or explicit pendinglimitation.','INC006 / PRB001','RESOLVED_SCENARIO'),
('DATA','MEDIUM','Duplicate transport review','Show sameeventkey and transportattempts versus currentvehicle.','Wrong deletion may corrupt audit.','Unique message/effect; duplicates remain in deliveryhistory.','INC007 / concurrencytest','RESOLVED_SCENARIO'),
('ACCESS','MEDIUM','BETA scope request','BETA cannot act for ALPHA/ZEE; investigate accountconfig.','One partner blocked; no scopewidening.','Correct ownerconfig,403/404 negative tests preserved.','INC008 / live02','RESOLVED_SCENARIO'),
('DATA','MEDIUM','Report grain contract','Confirm counting vehicles instead of events/deliveries.','Weekly report ambiguity.','Canonical aggregate accepted, badjoin regression proves distinction.','INC009 / PRB003','LAB_IMPLEMENTED'),
('INCIDENT','HIGH','503 availability rehearsal','Identify configfault versus runtimeabsence; preservejournal.','Portal tasks temporarily unavailable.','Health and bothsite smoke after auditedrecovery.','INC010 / live06','RESOLVED_SCENARIO'),
('REQUIREMENT','HIGH','Location correction','User wants faster correction; ask role/version/reason/audit.','Prevent silent lost update/wrong physical location.','Readerdenied,stale409,validsame-site update and audit.','BR001 / FR06 / live05','LAB_IMPLEMENTED'),
('REQUIREMENT','HIGH','Business hold controls','Clarify who can authorize physical release.','Safety-sensitive departure.','Operator sets hold; only approver releases with decision_ref; blockeddeparture.','FR07 / safetytest','LAB_IMPLEMENTED'),
('MAINTENANCE','MEDIUM','Fresh-target restore rehearsal','Run verified snapshot and restore to newDB, keep original.','Data loss risk during rollback.','Checksum recorded; overwrite denied;schema/index retained.','DbTool / Maintenance test','LAB_IMPLEMENTED'),
('CHANGE','HIGH','Independent ACK scheduling','Do not let callbacktimeout halt newdomainprocessing.','Backlog/confirmation may feed retries.','Two bounded schedulers and one-effectfailure tests.','CHG001 / PRB001','LAB_IMPLEMENTED'),
('CHANGE','MEDIUM','Add errorindex','Review V002 DDL and autocommit/recovery boundary.','Diagnosis throughput / schema risk.','Migration idempotent and EXPLAIN inspected, no data change.','CHG002 / Maintenance','LAB_IMPLEMENTED'),
('INVESTIGATION','HIGH','Real product inventory','Verify actual Oracle/AIX/JBoss/iWay/WebFOCUS/Apex versions.','Simulation limits must not hide enterprise risk.','Owners/version/lifecycle/sandbox documented; productclaims remain bounded.','platform-substitutions / onboarding','PROPOSED'),
('DOCUMENTATION','MEDIUM','Service Desk handover','Create task/site/time/ID evidence intake and next-update format.','Faster focused secondline without secretsharing.','Buddy can reproduce diagnosis from runbook.','on-call-handover / user-training','SCENARIO_COMPLETE'),
('MAINTENANCE','MEDIUM','Alert owner review','Assign oldestage/deadletter/ACK alertresponse; tune realworkload.','Healthyprocess may hide frozenchain.','CLI exitcodes and owner/action definition, expectedtrainingrejects explained.','monitoring alerts','LAB_IMPLEMENTED'),
('RELEASE','HIGH','WAR1.4.0 go/no-go','Buildhash/config/schema/mapping + UAT/recovery all needed.','Mixedversions or false readiness.','Actual deployacceptance and lifecycle/recovery recorded; only labapproval.','REL1.4.0 / WildFly','LAB_REHEARSED'),
('REQUIREMENT','HIGH','New-TOS cutovergate','Compare VIN/site/partner/location/state/version + in-flight plan.','Missing/mis-mappeddata may disrupt physicaloperation.','Badsnapshot exits2 NO_GO;goodsnapshot GO_LAB; realvendor migrationoutofscope.','cutover.py / cutover-rehearsal','LAB_IMPLEMENTED')]
ticket_json=[]
for i,(kind,priority,title,description,impact,ac,notes,status) in enumerate(tickets,1):
    id=f'TKT-{i:03d}';write(f'operations/tickets/{id}.md',f'# {id} — {title}\n\n**Type:** {kind}\n\n**Priority:** {priority}, based on illustrative impact; no ICO prioritypolicy.\n\n## Description\n{description}\n\n## Business impact\n{impact}\n\n## Acceptance criteria\n{ac}\n\n## Technical notes\n{notes}; linked evidence/runbooks in hiring guide.\n\n## Status\n{status}. Owner is a fictive role; execution status refers to lab or narrative, never a real customerticket. Follow-up: attach evidence, owner/date and validation beforeclosure.')
    ticket_json.append(dict(id=id,type=kind,priority=priority,title=title,status=status,path=f'operations/tickets/{id}.md',simulation=True))
write('operations/tickets/index.json',json.dumps(ticket_json,ensure_ascii=False,indent=2),False)
write('operations/changes/index.json',json.dumps([dict(id=id,path=f'docs/changes/{id}-{slug}.md',approval='PROPOSED_LAB_REHEARSAL',simulation=True) for id,slug,*_ in changes],indent=2),False)
write('operations/releases/index.json',json.dumps([dict(id='REL-1.4.0',path='docs/releases/REL-1.4.0.md',approval='LAB_REHEARSAL_ONLY',simulation=True)],indent=2),False)

# Machine-readable OpenAPI profile, with role restrictions and response semantics.
string=lambda **extra:dict(type='string',**extra)
event_schema=dict(type='object',additionalProperties=False,required=list(sample),properties={
'message_id':string(minLength=1,maxLength=64),'event_key':string(minLength=1,maxLength=64),'partner_id':string(enum=['ALPHA','BETA']),'site_id':string(enum=['ZEE','KAL']),'vin':string(pattern='^[A-Z0-9]{17}$'),'event_type':string(enum=['ARRIVAL','MOVE','DEPARTURE']),'location':string(minLength=1,maxLength=32),'event_at':string(format='date-time'),'expected_version':dict(type='integer',minimum=0)})
schemas={'PartnerEvent':event_schema,'Receipt':dict(type='object',required=['id','status','duplicate'],properties={'id':string(format='uuid'),'status':string(enum=['RECEIVED','RETRY_WAIT','PROCESSED','REJECTED','DEAD_LETTER']),'duplicate':dict(type='boolean')}),'Error':dict(type='object',required=['error','message','correlation_id'],properties={k:string() for k in ['error','message','correlation_id']}),'Correction':dict(type='object',additionalProperties=False,required=['expected_version','location','reason'],properties={'expected_version':dict(type='integer',minimum=0),'location':string(maxLength=32),'reason':string(minLength=1,maxLength=200)}),'Hold':dict(type='object',additionalProperties=False,required=['expected_version','hold','reason'],properties={'expected_version':dict(type='integer',minimum=0),'hold':dict(type='boolean'),'reason':string(minLength=1,maxLength=200),'decision_ref':string(minLength=1,maxLength=32)}),'Redrive':dict(type='object',additionalProperties=False,required=['reason'],properties={'reason':string(minLength=1,maxLength=240)}),'Controls':dict(type='object',additionalProperties=False,properties={**{k:dict(type='boolean') for k in ['worker_paused','dependency_unavailable','ack_timeout','force_api_failure']},'mapping_version':string(enum=['1','2'])})}
def operation(summary,roles,response='object',body=None,success='200',parameters=None):
    result=dict(summary=summary,description='Assumption / realistic simulation; role/site/partner restrictions enforced on server.',security=[{'BearerAuth':[]}],**{'x-allowed-roles':roles},responses={success:dict(description='Success; reception is not businesscommit',content={'application/json':{'schema':{'$ref':'#/components/schemas/'+response} if response in schemas else dict(type=response)}})})
    for code,desc in [('400','Malformed/validation'),('401','Token missing/invalid'),('403','Forbidden role/scope'),('404','Not found or outside scope'),('409','Idempotency/version/re-drive conflict'),('413','Body exceeds16KiB'),('429','Fixed-minute quota; Retry-After60'),('500','Internal failure, sanitized correlation'),('503','Sandbox dependency/readiness failure')]:result['responses'][code]=dict(description=desc,content={'application/json':{'schema':{'$ref':'#/components/schemas/Error'}}})
    if body:result['requestBody']=dict(required=True,content={'application/json':{'schema':{'$ref':'#/components/schemas/'+body}}})
    if parameters:result['parameters']=[dict(name=n,**{'in':'path'},required=True,schema=string()) for n in parameters]
    if response=='array':result['responses'][success]['content']['application/json']['schema']['items']=dict(type='object')
    return result
paths={
'/health':{'get':dict(summary='Actual DB readiness + app version',security=[],responses={'200':dict(description='READY'),'503':dict(description='DEGRADED'),'500':dict(description='Database dependency failure')})},
'/api/messages':{'post':operation('Durable reception; same key/payload duplicate200','PARTNER'.split(),'Receipt','PartnerEvent','202'),'get':operation('Scoped journal (max200 afterfilter)',['PARTNER','READER','OPERATOR','ADMIN'],'array')},
'/api/messages/{id}':{'get':operation('Status for receipt in ownscope',['PARTNER','READER','OPERATOR','ADMIN'],parameters=['id'])},
'/api/messages/{id}/redrive':{'post':operation('Reasoned re-drive of unprocessed failure only',['ADMIN'],'object','Redrive',parameters=['id'])},
'/api/vehicles':{'get':operation('Scoped current vehicles (max200)',['PARTNER','READER','OPERATOR','ADMIN'],'array')},
'/api/vehicles/{vin}/location':{'put':operation('Atomic same-site locationcorrection',['OPERATOR','ADMIN'],'object','Correction',parameters=['vin'])},
'/api/vehicles/{vin}/hold':{'put':operation('Set hold; release requires ADMIN plus decision_ref',['OPERATOR','ADMIN'],'object','Hold',parameters=['vin'])},
'/api/reports/occupancy':{'get':operation('Unique currentvehicle counts,allscopedrecords',['PARTNER','READER','OPERATOR','ADMIN'],'array')},
'/api/reports/occupancy.csv':{'get':operation('Same definition as JSON, CSV export',['PARTNER','READER','OPERATOR','ADMIN'])},
'/api/metrics':{'get':operation('Real cumulative/http/currentqueue metrics',['READER','OPERATOR','ADMIN'])},
'/api/audit':{'get':operation('Authorized audit, bounded200',['ADMIN'],'array')},
'/api/admin/controls':{'get':operation('Explicit local config/faultrows,defaults documented',['ADMIN'],'array'),'patch':operation('Audited local-only fault/configchange',['ADMIN'],'object','Controls')},
'/api/admin/diagnostics/{name}':{'get':operation('Allowlisted read-only diagnostics',['ADMIN'],'array',parameters=['name'])}}
paths['/api/messages']['post']['responses']['200']=dict(description='Existing receipt; unchanged businesspayload, duplicate=true',content={'application/json':{'schema':{'$ref':'#/components/schemas/Receipt'}}})
paths['/api/reports/occupancy.csv']['get']['responses']['200']=dict(description='site/partner/state counts as CSV',content={'text/csv':{'schema':string()}})
openapi=dict(openapi='3.1.0',info=dict(title='Terminal Flow Control simulation API',version='1.4.0',description='No actual ICO interface; synthetic data and loopback only. 16KiB requestlimit; strict JSON profile; businesscommit and signed callback are separate.'),servers=[{'url':'http://127.0.0.1:8090'},{'url':'http://127.0.0.1:8280/terminal-flow'}],paths=paths,components=dict(securitySchemes={'BearerAuth':dict(type='http',scheme='bearer',description='Generated local randomtoken, not JWT/OAuth')},schemas=schemas))
write('api/specifications/openapi.json',json.dumps(openapi,indent=2),False)
for name,value in [('request-arrival',sample),('response-received',dict(id='00000000-0000-4000-8000-000000000001',status='RECEIVED',duplicate=False)),('response-duplicate',dict(id='00000000-0000-4000-8000-000000000001',status='PROCESSED',duplicate=True)),('error-idempotency',dict(error='IDEMPOTENCY_CONFLICT',message='Same event_key with different business payload',correlation_id='example-request')),('ack-after-commit',dict(ack_id='00000000-0000-4000-8000-000000000001',event_key='ARR-001',partner_id='ALPHA',site_id='ZEE',status='PROCESSED',business_version=1))]:write(f'api/examples/{name}.json',json.dumps(value,indent=2),False)
write('api/README.md','''
# API exploration

OpenAPI3.1 spec is machine-readable JSON; examples are illustrative IDs, not logged customerresponses. Actual contract tested via tests/acceptance/test_live_api.py against local HTTP and same ServletWAR. Human contract/transport retry/error policy in docs/integrations/partner-contract.md. Auth: generated runtime keys, not exampleliteral. Use CLI `request ROLE METHOD /path [JSON]` to avoid keys in shared command examples.

Rate:120requests/actor/fixedminute,429Retry-After60. Body16KiB,syntax/type/extra/date400,scope403,changedpayload/version409. Timeout can occur after reception/commit; unchanged eventkey safely resolves receipt. Permanent input correction requires explicit partnerbusinessdecision, not making a freshkey to hide conflict. Businessreject status is asynchronous after202.

Offline schema/spec checks and online tests validate different layers; OpenAPI spec is not runtime enforcement itself. Production TLS/identity/standard/partnerURL unknown; all endpoints here are lab-only.
''')

requirements=json.loads((ROOT/'docs/role/requirements.json').read_text())
guide='''# Hiring manager guide — vijf minuten

Dit is een **Job Execution Repository / Role Operating System** voor de ICO IT Development Officer-vacature. Alle operationele rollen, historische tickets/incidenten/approvals en businesscase zijn **Assumption / realistic simulation**. Werkelijke uitvoerbaarheid wordt bewezen door broncode, tests en afzonderlijk geregistreerde testresultaten. Geen dienstverband/diploma/productexperience verzonnen.

## Snelle route

1. Bekijk requirements→proof hieronder: verantwoordelijkheid in plaats van random frameworks.
2. Start de verticale flow en herhaal een event: één business-effect, duidelijke journal/ACK.
3. Lees INC006/CHG001: waarom ACKtimeout niet dezelfde herstelactie is als mislukte commit.
4. Bekijk locatiecorrectie: rol,scope,version,reason,audit en holdbusinessdecision.
5. Bekijk werkelijk WAR/recovery/testbewijs en grenzen van H2/AIX/iWay/WebFOCUS/APEX-substituties.

| Vacaturevereiste | Concrete demonstratie / artefact | Bewijsgrens |
|---|---|---|
'''
guide+='\n'.join(f"| {r['id']} — {r['text']} | [{r['artifact']}](../{r['artifact']}) | {r['proof_type']} |" for r in requirements)
guide+='''

## Wat ik wel en niet aantoon

Wel: requirements, SQL/transaction/integration/security boundaries, concrete troubleshooting/control/report/release/recovery and stakeholderartefacts. Werkend Java/JDBC/HTTP/WAR-lab, meetbare negative/concurrency tests. Niet: echte Oracle/AIX/iWay/WebFOCUS/APEX-administratie, ICO-internalarchitecture, professionalexperience, taalniveau/diploma, availability or actualbudgetmandate. Ask candidate to demonstrate and explain own contribution; repository alone proves no unaidedmastery.
'''
write('docs/hiring-manager-guide.md',guide)
write('docs/testing/test-strategy.md','''
# Test strategy

Unit/domain/database:25 JUnit tests cover validation,strictJSON,date/type/extra/shape,canonicalbusinesskey,concurrentduplicates,hashconflict,partner/sitescope,atomicstate/event/audit/outbox,location/version/order/hold,rolecorrection,transientretry/exhaustion,ACKloss/HMAC/4xx,reportgrain and scopebeforelimit. Fresh in-memoryH2 pertest,closedaftertest; no productioncommand.

Integration/API:7Pythonacceptance tests against an actualrunninglocalserver and the sameWARonWildFly. Bothsites/signedACK;401/403/404/409;mappingredrive;pause/transientrecovery;portalcorrection/hold;503/readiness/adminrecovery;allowlistedSQL/CSV/reconciliation. Controlsresetaftercase; each message uses uniquesyntheticID. Fixedminute quota can matter if you run repeatedly; don't mislabel429 as serverbug.

Maintenance/regression:cutovergood/bad/duplicates;H2migrationtwice,backupsnapshot,nooverwrite,freshrestore,index/schema retained. Additional structural audit validates every R-IDpath,incident/runbook/ticketrequiredfields,OpenAPI schema/examples/APIpaths,mirroredSQL/schema,links and no obvioussecretpatterns. These are meaningful contentcontracts, not a claim of fullstaticanalysis.

Browser:2Playwright tests exercise auth/scopeddisplay,readerwritefail,partnerposting,operatorview,errorfeedback,logoutandmobile390px. Token input password/inmemory; no realcredential screenshot. Browser/IAB unavailable in executionenvironment, so Chromiumfallback explicitly recorded. UI+APIproof supplement each other; no pixel-designclaim.

Release/smoke:health and end-to-end two-sites event/dedup/ACK/reconciliation. Productionvalidation requires actualmandaat/allowedtestdata/config/scope and agreedmonitorwindow. Oracle/AIX/vendorproducts not tested; performancequeryplan is real but scale/SLA/speedup notclaimed. Missing enterpriseidentity/TLS/HA explicitly known.
''')

write('.github/PULL_REQUEST_TEMPLATE.md','''
## Business problem / resulting behaviour
RequirementIDs / CRQ:

## Scope and evidence
- Acceptance/negative/concurrency/recovery tests:
- Component/schema/mapping/partnercontract impact:
- Role/scope/safety/audit impact:

## Release / recovery
- Target/config/secretrefs (no values):
- Deploymentorder and manifest:
- Rollback/forwardfix/data/in-flight boundary:
- Usertraining/ServiceDesk handover:

## Remaining risks / decisions
Explicitowner/mandaat; simulation vs actualproof. No fabricatedapprovals.
''',False)
for slug,title,body in [('bug_report','Bug / incident','Task/site/partner/time/correlation; expected/actual; impact/safety; lastgoodboundary; hypotheses/tests; no tokens; validation/owner/nextupdate.'),('change_request','Change / CRQ','Businessgoal/in-outscope; R-ID; dependencies/risks; implementation/test/UAT; recovery; window/decisionowner; actualevidence; no fictionalapproval.'),('documentation','Documentation / knowledge gap','Which role/task lacksusableinstruction? Existingpath/version; actualexample; source/assumption; teach-back/acceptance and owner/date.')]:write(f'.github/ISSUE_TEMPLATE/{slug}.md',f'---\nname: "{title}"\nabout: "Operationally useful {title.lower()} record"\n---\n\n{body}',False)

print(json.dumps(dict(requirements=len(requirements),incidents=len(incidents),problems=len(problems),changes=len(changes),runbooks=len(runbooks)+1,tickets=len(tickets),diagnostics=len(queries)),indent=2))
