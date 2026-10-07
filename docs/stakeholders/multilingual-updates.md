# N / E / F — operational communication samples

Vacature zegt N/E/F; interpretatie Nederlands/Engels/Frans en gewenst niveau moeten bevestigd worden. Dit bewijst documentvoorbereiding, geen persoonlijke spreekvaardigheid.

**NL:** “Het bericht is ontvangen, maar nog niet verwerkt. We controleren de mapping en de huidige voertuigstatus. Gelieve dezelfde businessreferentie te behouden bij een retry. Volgende update om10:30UTC.”

**EN:** “The message was received but has not been processed. We are checking the mapping and the current vehicle state. Please keep the same business reference for any retry. Next update at10:30UTC.”

**FR:** « Le message a été reçu, mais il n’a pas encore été traité. Nous vérifions le mapping et l’état actuel du véhicule. Veuillez conserver la même référence métier lors d’une nouvelle tentative. Prochaine mise à jour à10h30UTC. »

Actionlog always owner/date/expectedoutput; confirm shared meaning of receipt/commit/ACK across languages. Recipient repeats expectedaction, not just “understood”.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
