# PRB-001 — ACK-fouten keren terug; retries blokkeren bij één thread mogelijk nieuwe businessverwerking.

## Problem statement / business impact
Partner ziet onzeker resultaat en kan redundante input sturen; backlog en verkeerde herstelactie riskeren.

## Timeline
Fictieve cyclus: eerste incident week1 → herhaling week2 → RCA week3 → approved workpackage week4 → regression/nazorg week5. Exacte corporate historie niet geclaimd.

## Root cause analysis / 5 Whys
Callback/path tijdelijk unavailable → ACKsend fails → confirmationretry nodig → business/outbound waren onvoldoende onderscheiden → health/contract gaf geen expliciet effectbewijs.

## Contributing factors
Ontbrekend commit/ACK-datacontract en shared scheduling vergroten onduidelijkheid; no exactly-once-network delivery.

## Permanent corrective action
Durable outbox, independent processing/ACK scheduler, stable ack_id receiverdedup, bounded retries + alert; CHG-001. Simulated owners: officer coördineert; developer/integrationpartner levert testbaar werk; business accepteert definitie/gedrag; supervisor autoriseert change.

## Verification / prevention
INC-006/INC-010; JUnit response-loss + live outbox evidence; callbackfirstfailure vs dataeffects afzonderlijk. Open action owners en acceptance in release1.4.0. Preventie is pas afgesloten als herhaling met regressie/monitoring wordt gedetecteerd of voorkomen. Geen “menselijke fout” als eindoorzaak.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
