# Technical project plan / work packages

Scope: reliable partner event → terminal record → report → ACK plus operational controls. Out of scope: real ICO interfaces, hardware, enterprise identity, ship planning and high availability. Method: businesscase, staged delivery, workpackages, acceptance and escalation tolerances (PRINCE2-compatible thinking; no certificate claim).

| WP | Output / owner (simulated) | Dependency | Acceptance |
|---|---|---|---|
| WP1 | Business rules / key user + analyst | Stakeholder interviews | BR/FR and safe hold decision accepted |
| WP2 | Contract/schema / developer | WP1 | Constraints + contract negative tests |
| WP3 | Worker/outbox / integration partner | WP2 | Duplicate/timeout/partial-commit tests |
| WP4 | Portal/report / app team | WP2 | Role/version UAT, correct vehicle counts |
| WP5 | Release/recovery / officer + runtime owner | WP3/4 | WAR deploy, hash, smoke and restore rehearsed |
| WP6 | Training/operations / officer + Service Desk | WP5 | Runbooks, teach-back, handover and alertowner |

Milestones: M1 acceptance definition; M2 vertical flow; M3 failure lab; M4 UAT and recovery; M5 lab release/nazorg. Risk tolerances are simulation choices: escalate ≥10% forecast cost drift, missing safety/data gate immediately, critical acceptance failure as no-go. Workpackage acceptance differs from developer-complete. Actual fictive capacity/budget numbers in operations/portfolio, never claimed as ICO budget.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
