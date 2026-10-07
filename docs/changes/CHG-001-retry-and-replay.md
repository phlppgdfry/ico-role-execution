# CHG-001 — Onafhankelijke verwerking, durable outbox en begrensde retries

## Aanleiding / impact
INC-006 / PRB-001; input en ACK mogen elkaar niet verkeerd herhalen. Java Worker/Application scheduling, outbox, partnercallback en alert/runbook; geen userdatacontractremove.

## Scope / risico
Dubbele delivery, partial commit, verkeerde retry van permanent4xx; singleinstance blijft beperking. In scope bovenstaande componenten; out of scope echte ICO-app/Oracle/AIX. Stopcriteria: unexplained data diff, authorization gap, missing recovery or critical UAT failure.

## Implementation plan / work packages
Implement message/ACK separatie en 5-attempt1–16s delays; two independent scheduled tasks; receiver stable-ID/HMAC; logging aftercommit. Owner: lab developer/integration role; officer coördineert acceptance en dependencies.

## Test plan
JUnit lost ACK/transient/deadletter/concurrency + live partner callback. Test permanent4xx and no businessrepeat. Include happy, negative, concurrency and recovery; attach actual output, not checkbox only.

## Rollback / recovery
Stop consumers within mandaat, preserve journal/outbox, revert compatible WAR if schema unchanged. Never re-import PROCESSED to forceACK.

## Approval / deployment window
Simulated request to IT Supervisor + businessowner; approval record status **PROPOSED / lab rehearsal**, not real approval. Illustrative window 2026-09-28 16:00–17:00 UTC, conditional on stable operations and available vendor/data/runtimeowners. Budget/capacity in projectforecast. No actual message sent.

## Verification / closure
Businessloop and callback receipt; reconciliation empty; attempts bounded; audit of any redrive. Releaseowner records hash/config/schema/mapping, known issues and nazorgowner. Businessacceptance and technical validation separate.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
