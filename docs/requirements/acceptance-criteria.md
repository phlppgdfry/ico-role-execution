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

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
