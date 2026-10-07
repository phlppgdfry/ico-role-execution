# CHG-003 — Gereviewde locatiealiases met gecontroleerde redrive

## Aanleiding / impact
INC-005 / PRB-002; partnerformat agreed alias ontbreekt in mapping1. Current mappingcontrol2; ZEE/KAL codevariant, inputjournal, rejected messages and audit.

## Scope / risico
Te brede normalisatie, wrongsite, verwerking van reeds gecommitteerd event of partnerreplay with altered payload. In scope bovenstaande componenten; out of scope echte ICO-app/Oracle/AIX. Stopcriteria: unexplained data diff, authorization gap, missing recovery or critical UAT failure.

## Implementation plan / work packages
Partner/keyuser bevestigen exact aliases; enable mapping2 by admin; test invalid/wrongsite; list rejected IDs; reasoned redrive only allowable statuses. Owner: lab developer/integration role; officer coördineert acceptance en dependencies.

## Test plan
mappingFixAndAuthorizedRedriveAreAudited; HTTP03; siteconstraint, version/hold rules unchanged; negative unknownalias. Include happy, negative, concurrency and recovery; attach actual output, not checkbox only.

## Rollback / recovery
Set mapping1 again; leave historic processed records/audit intact. Back-out newly created businessdata is separate authorized correction, not automatic mappingrollback.

## Approval / deployment window
Simulated request to IT Supervisor + businessowner; approval record status **PROPOSED / lab rehearsal**, not real approval. Illustrative window 2026-09-28 16:00–17:00 UTC, conditional on stable operations and available vendor/data/runtimeowners. Budget/capacity in projectforecast. No actual message sent.

## Verification / closure
Affected IDs one event/outbox each, UNKNOWN_LOCATION only for truly invalid codes, partnerACK and scoped inventory checked. Releaseowner records hash/config/schema/mapping, known issues and nazorgowner. Businessacceptance and technical validation separate.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
