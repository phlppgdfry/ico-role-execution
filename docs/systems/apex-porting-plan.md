# Apex — assumed Oracle APEX: porting work package

Vacancy says Apex alongside Oracle; productinterpretation remains unconfirmed. No fake APEX export that cannot be imported/tested. The working HTML portal demonstrates the requested behaviour; this document specifies actual APEX work if confirmed.

Target pages: scoped vehicle report, detail/current version, location correction with reason, audit inspection for authorized owner. Regions/items: VIN, site/partner, location select from active same-site masterdata, expected_version and reason. Server-side validations and authorization schemes required; hidden buttons alone insufficient. Use existing TOS/API boundary if direct DB ownership would violate systemcontract.

Request route for actual Oracle APEX may be browser → ORDS/weblaag → APEX engine/PLSQL → Oracle. ORDS is not named in vacancy and is not assumed to run on the JBoss path. APEX session is not permanently the same DB session. Auth/productversion/workspace/deployment/export format must be confirmed.

Acceptance: reader direct correction denied; wrong site/code fails without change; stale version asks reload; successful correction records actor/old/new/reason/time; key user performs task without instructor. Porting evidence required: actual export/import, productversion, authorized sandbox, automated/manual role tests and deployed flow. Until those exist the repository proves task design and equivalent implementation, not APEX productexperience.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
