# Quality / safety / environmental support

Vacature vraagt ondersteuning van kwaliteits-, veiligheids- en milieumanagement. Concrete interne normen/certificaten onbekend. Simulatie: softwarevrijgave mag geen fysieke toestemming suggereren zonder businessbesluit; holds blokkeren vertrek, audit maakt correcties traceerbaar en operator kan hold niet zelfstandig verwijderen. Een IT-medewerker is niet automatisch operationeel releaseowner.

Quality gate: receipt/event/outbox reconciliation, locatie-/site-validatie, negatieve UAT en reproducerbare release. Veiligheidsworkaround moet eigenaar, beperkingen, einddatum en latere reconciliatie hebben. Bij statusconflict fysieke handeling pauzeren via bevoegde operationsowner, niet blind UPDATE toepassen. Milieu: betrouwbare rapportdefinities/efficiënte informatie kunnen processen ondersteunen; repo berekent geen fictieve emissie-KPI of certificering.

Voorstel verbetering: detecteer herhaalde statuscorrecties per proces en bespreek bronoorzaak met key user; automatiseer read-only controles zodat minder handmatige herinvoer nodig is. Effect eerst echt meten, geen verzonnen percentages.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
