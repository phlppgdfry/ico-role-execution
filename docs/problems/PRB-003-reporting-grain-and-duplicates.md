# PRB-003 — Herhaalde meldingen “dubbele data” door telling van afleverpogingen of historyevents.

## Problem statement / business impact
Onbetrouwbare operationele rapportinterpretatie; onnodige risicocorrecties en stakeholderwantrouwen.

## Timeline
Fictieve cyclus: eerste incident week1 → herhaling week2 → RCA week3 → approved workpackage week4 → regression/nazorg week5. Exacte corporate historie niet geclaimd.

## Root cause analysis / 5 Whys
Totaal verschillend → one-to-many join → verkeerde grain gekozen → rapportbusinessobject niet geaccepteerd → syntax/test alleen happy sample zonder duplicates.

## Contributing factors
Eventtijd versus verwerkingstijd, scope en refresh kunnen extra verschillen veroorzaken; eerst dezelfde snapshot.

## Permanent corrective action
BR07 vehiclegrain, canonical occupancyquery/CSV, duplicate/multisite regression and businessdefinition signoff. Simulated owners: officer coördineert; developer/integrationpartner levert testbaar werk; business accepteert definitie/gedrag; supervisor autoriseert change.

## Verification / prevention
INC-007/INC-009; anti-pattern test proves two deliveries versus one vehicle; no delete/DISTINCT workaround. Open action owners en acceptance in release1.4.0. Preventie is pas afgesloten als herhaling met regressie/monitoring wordt gedetecteerd of voorkomen. Geen “menselijke fout” als eindoorzaak.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
