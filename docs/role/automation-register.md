# Automation register

| Manual → automated | Working command | Benefit / safety |
|---|---|---|
| Repeated health/openroute check → healthCLI | manage.py health | Actual200/503, exit1 onfailed; read-only |
| Scrolljournals forfailedinputs → allowlisted SQLinventory | manage.py failed | Reject/retry/deadletter separated; read-only |
| Guessbacklogimpact → metricthresholdalerts | manage.py alerts | Owner/action, exit2 activealerts; no fakeSLA |
| Handcomparecommit/outbox → invariantquery | manage.py reconcile | Keyconsistency,exit2differences,notbulkcorrect |
| Repeated deploymentchecking → businesssmoke | manage.py smoke | Newsyntheticevents bothsites+duplicateproof; explicitmutation |
| Readlogmanually → JSONeventsummary | manage.py log-summary | No secret/rawpayload; countersnotrootcause |
| CopyunversionedWAR → hashmanifest | manage.py release-manifest | SHA/version/revisionproof,local file only |
| Countmigrationrows → cutoverkey/fieldgate | cutover.py source target | Exit2diffs prevents falsereadiness |

Do not automate destructivecorrection or businessrelease without decision/mandaat. Scripts have explicit target/role, bounded requests and documentedexitcodes. Production benefits require realbaseline, not illustrative time-savingpercentage.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
