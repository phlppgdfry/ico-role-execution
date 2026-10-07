# BR-001 — Controleerbare terminaldatastroom

## Vage vraag → probleem
“We willen dat partnerberichten sneller en zonder dubbel werk in het terminalscherm komen.” Analysevragen: welke taak blokkeert, hoeveel unieke voertuigen/events, welke vestiging/partner, wat is ontvangen versus verwerkt, welke fysieke status klopt? Fictieve as-is: e-mails en handmatige herinvoer, geen gezamenlijke correlation-ID, transporttimeout leidt tot dubbel verzenden. Niet als ICO-feit lezen.

## Gewenste situatie / stakeholders
Operations kan locatie/status/audit vertrouwen. Partner krijgt een receipt en later business-ACK. Development officer kan eerste foutgrens en backlog onderzoeken. IT supervisor autoriseert change/release binnen scope; business approver beslist fysieke vrijgave. Service Desk verzamelt scope en eskaleert naar tweede lijn; leveranciers leveren contract/mapping- en runtimesupport. Zie RACI.

## Business outcomes
BR1: één business-effect per partner/eventkey. BR2: zichtbare verwerking en verklaarbare afwijzing. BR3: beide sites geïsoleerd correct. BR4: correcties met actuele versie, reden en audit. BR5: hold beschermt vertrek, vrijgave vraagt bevoegde beslissing. BR6: herhaalbare recovery en release-evidence. BR7: rapporten tellen unieke voertuigen en gebruiken afgesproken snapshot/definitie.

Geen verzonnen ROI/SLA. Labdoelen in NFR zijn testbare eigen ontwerpkeuzes. Acceptatie betekent succesvolle én negatieve taaktests plus geaccepteerde beperkingen, geen mooi scherm alleen. Requirementscope: synthetische voertuigen en twee partners; niet shipplanning, finance, douane of echte PDI/ERP.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
