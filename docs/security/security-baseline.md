# Security baseline

Authentication: five distinct random bearer tokens generated into runtime/.env (0600), minimum 24 chars, comparison via MessageDigest.isEqual. No production/default secrets. Authorization: PARTNER submits own partner/site and reads own rows; READER reads/report/metrics; OPERATOR corrects location and sets hold; ADMIN releases hold with decision_ref, re-drives failures, views audit and controls. This is a lab rolemodel, not employment mandate or enterprise SSO.

Least privilege: role/server/object scope enforced, outside detail scope 404. SQL filters precede list limits. Bound queries and fixed diagnosticallowlist; no arbitrary SQL endpoint. 16 KiB requests, fixed minute actor quota and bounded DB/callback timeouts. Secrets never in URL/log/bodyexamples or Git; portal keeps token only in memory. Clear action removes token/loaded data. Runtime directory private, file DB has no TCP listener and empty embedded sa password is acceptable only under local file/OS boundary.

Integrations: exact payload HMAC SHA256, callback allowlisted to loopback, redirects denied, receiver dedups stable ack_id. HTTP allowed only in local lab. Production needs TLS/cert/trust, identityprovider, keyrotation, serviceaccounts with owner/expiry, storageencryption/retention and incidentprotocol. No security certification or penetration-testclaim.

Sensitive data: synthetic IDs only; real VIN/customerdata must not be added. Logs deliberately omit payload/secrets; audit access adminonly. Token leak: stop affected lab, regenerate runtime credentials under approved local owner, restart both services and retest roles/HMAC. No actual notifications or submissions to ICO.

Threats: scope spoofing (deny), duplicate/concurrent event (unique/hash), changed payload (409), unauthorized direct UI bypass (server deny), secret log exposure (no token logs), oversized body/quota, ambiguous physical release (businessapprover). Remaining lab limits: no TLS, MFA, sophisticated tokenmanagement, HA, distributed limiter or hardened internet exposure. Do not host this mutation API publicly.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
