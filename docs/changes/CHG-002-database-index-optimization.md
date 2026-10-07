# CHG-002 — Additieve errorlookup-index

## Aanleiding / impact
INC-003; diagnosequery bij fouten moet een beoordeeld indexpad hebben. V002 error index/schema_version2, diagnostics; geen table/data transformation.

## Scope / risico
DDL autocommit, filelock, workload-specific plan; geen gegarandeerde speedup. In scope bovenstaande componenten; out of scope echte ICO-app/Oracle/AIX. Stopcriteria: unexplained data diff, authorization gap, missing recovery or critical UAT failure.

## Implementation plan / work packages
Stop lab app; snapshot; copy reviewed V002 inside runtime; DbTool migrate; compare schema_version and EXPLAIN; restart/validate. Owner: lab developer/integration role; officer coördineert acceptance en dependencies.

## Test plan
Fresh DB migration applied twice safely; capture actual plan; same dataset/time and query if measuring speed. Include happy, negative, concurrency and recovery; attach actual output, not checkbox only.

## Rollback / recovery
Index mag achterblijven bij approllback; only remove via reviewed follow-up. Restore snapshot to fresh target for genuine data recovery, not blind overwriting current DB.

## Approval / deployment window
Simulated request to IT Supervisor + businessowner; approval record status **PROPOSED / lab rehearsal**, not real approval. Illustrative window 2026-09-28 16:00–17:00 UTC, conditional on stable operations and available vendor/data/runtimeowners. Budget/capacity in projectforecast. No actual message sent.

## Verification / closure
Schema2 present, constraints/data unchanged, diagnostic query/smoke pass; actual performance claim only if measured. Releaseowner records hash/config/schema/mapping, known issues and nazorgowner. Businessacceptance and technical validation separate.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
