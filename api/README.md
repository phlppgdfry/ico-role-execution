# API exploration

OpenAPI3.1 spec is machine-readable JSON; exemplos are illustrative IDs, not logged customerresponses. Actual contract tested via tests/acceptance/test_live_api.py against local HTTP and same ServletWAR. Human contract/transport retry/error policy in docs/integrations/partner-contract.md. Auth: generated runtime keys, not exampleliteral. Use CLI `request ROLE METHOD /path [JSON]` to avoid keys in shared command examples.

Rate:120requests/actor/fixedminute,429Retry-After60. Body16KiB,syntax/type/extra/date400,scope403,changedpayload/version409. Timeout can occur after reception/commit; unchanged eventkey safely resolves receipt. Permanent input correction requires explicit partnerbusinessdecision, not making a freshkey to hide conflict. Businessreject status is asynchronous after202.

Offline schema/spec checks and online tests validate different layers; OpenAPI spec is not runtime enforcement itself. Production TLS/identity/standard/partnerURL unknown; all endpoints here are lab-only.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.

