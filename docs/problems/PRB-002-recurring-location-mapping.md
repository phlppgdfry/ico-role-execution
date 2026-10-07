# PRB-002 — Nieuwe locatiecodevarianten veroorzaken herhaalde rejects.

## Problem statement / business impact
Afgebakende partner/siteflow vertraagd, handmatig “fixen” kan fysieke locatie vervalsen.

## Timeline
Fictieve cyclus: eerste incident week1 → herhaling week2 → RCA week3 → approved workpackage week4 → regression/nazorg week5. Exacte corporate historie niet geclaimd.

## Root cause analysis / 5 Whys
Codevariant niet bekend → master/mappingreject → contractsample niet afgestemd → versiechange niet als releaseafhankelijkheid → geen gezamenlijke owner voor codecatalog.

## Contributing factors
Vendorcontract ontbrekende voorbeelden en sitevarianten; verkeerde fallback zou probleem verbergen.

## Permanent corrective action
CHG-003 reviewed aliases, masterdatarevalidation, bothsite-negative tests, reasoned redrive and vendorhandshake. Simulated owners: officer coördineert; developer/integrationpartner levert testbaar werk; business accepteert definitie/gedrag; supervisor autoriseert change.

## Verification / prevention
INC-005; actual mapping/redrive tests; audit + one effect; reject validunknowncodes remains enforced. Open action owners en acceptance in release1.4.0. Preventie is pas afgesloten als herhaling met regressie/monitoring wordt gedetecteerd of voorkomen. Geen “menselijke fout” als eindoorzaak.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
