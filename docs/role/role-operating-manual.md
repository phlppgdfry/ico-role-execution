# Role operating manual — zo voer ik de rol uit

## Morning routine
08:30 overdracht/incidentowner controleren; veiligheidsimpact en open productiehandelingen bespreken. Health plus backlog/oldest pending en ACK-inventory bekijken, niet alleen groen proces. Service Desk-ticket moet site/partner/tijd/expected-versus-actual/repro/ID bevatten. Actieve incidenten vóór projecten op impact/urgentie prioriteren. Lees vendoracties en releasekalender; reserveer capaciteit voor interrupts.

## During the day
Eén owner per ticket, meerdere hypotheses met onderscheidend bewijs. Volg gebruiker → API → journal → mapping → commit → ACK → rapport. Read-only checks eerst; veranderingen met mandaat/CRQ en herstelplan. Behoeftenanalyse begint bij taak/uitzondering; technical specs omvatten roles, data, interfaces, foutpaden, acceptance en afhankelijkheden. Vendor krijgt werkpakket en objective acceptance, geen “maak het werkend”. UAT met key user zelf laten uitvoeren; documentatie/training zijn deliverables.

## End-of-day checks
Geen half deployment zonder overdracht. Backlog/difference sets/ACK na herstel opnieuw meten. Tickets sluiten pas na businessvalidatie; onzekere oorzaak naar problem met owner. Vastleggen: actie/tijd/uitkomst, open risico, volgende stap/eigenaar/update. Kritieke credentials/toegang/escalatiedekking vóór wachtdienst controleren. Geheimen niet in werknotities.

## Weekly responsibilities
Portefeuille en accepted delivery tegenover baseline; capacityforecast/actual/remaining cost; afwijkingen vroeg met opties melden. IT/businessweekrapport heeft resultaat, impact/risico, besluit, owner en datum. Releaseafhankelijkheden tussen app/schema/mapping/partner bevestigen. Eén terugkerend incident voor prevention kiezen; één runbook/quick guide valideren met collega. Taal N/E/F op doelgroep afstemmen.

## Monthly responsibilities
Componentcatalogus/lifecycle/supportstatus, vendorservice/contract en capacitytrend bespreken. Rehearsal van herstel/backup en één end-to-end foutscenario. Audit van toegangsrechten/secretowners/retention met echte securityowner. Projecttoleranties en trainingsplan bijwerken. Datakwaliteit/rapportdefinities met business bespreken; tijdwinst alleen met baseline claimen.

## Critical-event behaviour
Veiligheid/impact eerst, incidentowner en vaste updatecadans. Beperk scope, preserveer evidence, geen parallelle tegenstrijdige fixes. Escaleer data/security/mandaatgrens en specialistbehoefte vroeg. Workaround heeft owner/beperking/einddatum/reconciliatie. Stop/no-go bij onbekende migratiestaat of ontbrekend recoverybewijs. Communiceer feit/onbekend/actie/volgende update; geen onbewezen ETA. Root cause vereist bewijs en tegenhypothese, geen schuldnaam.

## Ownership
Ik ben verantwoordelijk voor gecontroleerde uitkomst binnen afgesproken domein, niet alleen mijn codetaak. Ik volg acceptance, training, nazorg en overgedragen acties. Budget-/go-live-/fysieke-vrijgavemandaat komt van bevoegde owners. Alle daadwerkelijke ICO-eigenaren, versies, tools en rooster moeten intern bevestigd worden.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
