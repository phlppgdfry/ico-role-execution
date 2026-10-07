# New-terminal-system cutover rehearsal

Fictief oud/nieuw datamodel is dezelfde businesskey/statevariant, niet een genoemd ICO-product. Exercise: source snapshot → target migration result → key/field reconciliation → go/no-go → route/in-flight handling → businessvalidation. Cutover script checks snapshots, does not pretend to perform a real vendor migration.

`python3 deployment/scripts/cutover.py deployment/environments/source-snapshot.json deployment/environments/target-bad.json` must fail with missing/wrong key. Correct target passes. Compare VIN, partner/site,location,state,version; countonly is insufficient. Empty snapshots, duplicatekeys or unexpectedfields are rejected. Script output is concrete JSONdifference report and exitcode2 on mismatch.

Production-like steps: freeze/snapshot agreed with business; durable inventory of in-flight partner events and last processedkey; migrate history/status/masterdata; compare same cutoff; stopgo-live on unexplaineddiff; preserve oldroute until decision; switch partnerroute; apply delta with duplicate-safe keys; verify physical/business state and ACK; retain exit/recoverywindow. Restoring oldsnapshot can lose newerchanges, so no unsupported zero-loss claim.

This repository actually tests H2 backup/freshrestore and keydiffgate; it does not operate a real new ICO TOS. Open product/mapping/history/RPO/RTO questions remain on onboarding agenda.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
