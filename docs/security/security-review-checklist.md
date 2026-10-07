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

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
