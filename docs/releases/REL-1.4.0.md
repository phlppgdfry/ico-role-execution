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

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
