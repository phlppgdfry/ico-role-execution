# Partner contract / interface ownership

Owner roles: partner sender owns valid business event/key; integration team owns mapping, receiptjournal, processing and ACK; business owns transition/hold definition; runtime/data owners support resources. Real vendor/standard unknown. JSON schema in OpenAPI is canonical external contract; edi samples are synthetic testfixtures.

Transport POST /api/messages uses partner bearer and strict site/partner scope. 202 = received durably, not processed. GET receipt follows status. 200 duplicate may refer to RECEIVED, PROCESSED or rejected prior event; never interpret it as new businesssuccess. 409 idempotency conflict requires sender investigation, not new key to hide inconsistency. 400/403/413 nonretryable without correction; 429 obey Retry-After and preserve same business key; 5xx/timeout retry bounded with same key and unchanged payload.

Client timeout after reception may repeat safely. Business processing uses 5 attempts, exponential 1–16s delay for the explicitly transient dependency; permanent rules become REJECTED. Admin redrive requires reason and is forbidden for PROCESSED/RECEIVED. Callback comes after commit, is signed over exact UTF-8 body, and uses stable ack_id. Receiver persists dedupreceipt before returning 200. ACK network loss can cause duplicate delivery, not duplicate businessmutation.

Partner data model: arrival/version0; current-version move; current-version departure with location/hold rules. Event timestamp must increase for an existing vehicle. A retry does not change timestamp/version/location. Codechange/mapping requires sample exchange, version decision, acceptance and coordinated release. Evidence pack includes system receipt ID, partner/event key, transport ID, timestamp/zone, mappingversion, first failure and expected result; no tokens/raw sensitive payload in email.

External networking/TLS not verified in this lab. Callback allowlist deliberately permits only localhost/127.0.0.1; production integration needs HTTPS, certrotation, identity/replay policy and actual vendor agreement. Browser cross-origin mutation is not enabled.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
