# Vacancy analysis — ICO IT Development Officer

Bron: [volledige vacature](https://www.icoterminals.com/nl/jobs/it-development-officer), opnieuw gelezen 7 oktober 2026. Geen interne toegang. Artefacts en fictieve historie zijn **Assumption / realistic simulation**. Geen bewijs van dienstverband of gerealiseerde resultaten bij ICO.

## Functie

ICO / International Car Operators; RoRo/automotive maritieme logistiek uit publieke bedrijfscontext. Locatie Zeebrugge, verantwoordelijkheid Kallo én Zeebrugge. Onbepaalde duur, 38 uur, dagshift, korte verplaatsingen 1–2 maal per maand, Service Desk-wachtdienst. IT-master of bachelor gelijkgesteld door ervaring. Senioriteit is niet letterlijk benoemd: brede zelfstandige verantwoordelijkheid wordt gevraagd, geen bewezen minimum jaren.

Rapporteert aan IT Development Supervisor en Director IT. Sturing aan intern/extern ontwikkelingsteam en partners; projectcoördinator, businessunits, klanten en leveranciers als contacten. Teamgrootte onbekend.

Doel: technische projecten specificeren/plannen/beheren/rapporteren, externen sturen, core-systemen beheren en nieuw Terminal Systeem en applicatieve vernieuwing realiseren. Ook kwaliteit, veiligheid en milieu ondersteunen.

## Volledige verantwoordelijkheden en bewijsgrenzen

Dagelijks: prioriteren/afsluiten tweede-lijnstickets, interfaces/core beheren, samenwerken, documenteren. Projectmatig: behoeftenanalyse, technische specs toetsen aan strategie/procedures, lastenboek/CRQ/werkpakketten, implementatie/outsourcecoördinatie, capaciteit/budget en afwijkingen. Applicatief: modelling, releases over servers/systemen, TOS-gerelateerde systemen, EDI/rapportering, webportalen en nieuwe functionaliteit/koppelingstools. Wekelijks: rapportage IT/business. Mensen: gebruikersopleiding en nieuwe collega’s trainen. Infrastructure/security/auth/monitoring/deploymentdetails zijn noodzakelijke simulatiekeuzes, niet volledige infrastructuurrol of bewezen ICO-tooling.

Arbeidsvoorwaarden vermeld: maaltijd/ecocheques, groeps- en hospitalisatieverzekering, GSM/laptop, firmawagen, onkostenvergoeding, cafetariaplan en opleidingsmogelijkheden. Dat zijn arbeidscontext en gesprekspunten, geen uitvoerbare engineeringcompetenties. Diploma/feitelijke taalvaardigheid/availability bewijst deze repo niet.

## Alle technologische categorieën

| Categorie | Expliciet uit vacature | Assumption / realistic simulation |
|---|---|---|
| Programmeertalen | Geen expliciete programmeertaal; N/E/F zijn menselijke talen | Java 21, Python 3, kleine vanilla JS-portal |
| Database | Oracle | H2 met JDBC, Oracle-compatibility mode; geen echte Oracle-test |
| OS/hardware | AIX / IBM P-series | Lokale macOS/Linux; AIX-runbook beperkt tot conceptoverdracht |
| Application server | JBoss | Echt Servlet-WAR; WildFly 39 als reproduceerbare JBoss-familie labserver |
| Framework | Apex genoemd, waarschijnlijk Oracle APEX | Portal-equivalent + portingplan; geen fictief APEX-export |
| API/protocol | Geen API-type of EDI-standaard benoemd | JSON-over-HTTP en OpenAPI 3.1; HMAC-ACK |
| Middleware | iWay | In-process integration worker met mapping, retries en message journal |
| EDI | EDI-processing | Afgesproken JSON-profiel; geen EDIFACT-certificatieclaim |
| Reporting | WebFOCUS | SQL/CSV-rapporten met definities en reconciliatie |
| Messaging | Niet gespecificeerd | Databasequeue + outbox, één actieve workerinstance |
| Cloud / CI/CD | Niet gespecificeerd | GitHub Actions CI; geen public cloud of Kubernetes |
| Monitoring/logging | Niet gespecificeerd | JSON-events, actuele metrics en alerts CLI |
| Auth/security/network | Niet gespecificeerd | Bearer role/scope, least privilege, loopback defaults, HTTP alleen lokaal |
| Planning/productiviteit | PRINCE2 of alternatief; MS Office | Werkpakketten/risicolog/CSV-budget; Excel/Word-compatibele artefacts |

## Vacancy → Responsibility Matrix

| ID | Vereiste (parafrase) | Werkelijke verantwoordelijkheid | Uitvoering / afbakening |
|---|---|---|---|
| R01 | Permanente functie, Zeebrugge, 38 uur | Een vaste rol met planning over meerdere projecten. | Plan capaciteit op 38 uur; reserveer interruptieruimte. |
| R02 | IT-master of bachelor gelijkgesteld door ervaring | Toon theoretische basis én toepasbare ervaring; precieze diploma-equivalentie navragen. | Koppel opleiding en projecten aan analyse, systemen en delivery. |
| R03 | Dagshift, beperkte verplaatsingen en wachtdienst | Regulier dagwerk met beschikbaarheidsverplichtingen; rooster onbekend. | Vraag oproepfrequentie, compensatie, toegang en escalatiedekking. |
| R04 | Integriteit, intensiteit, innovatie | Eerlijk rapporteren, zorgvuldig afwerken en nuttig verbeteren. | Meld risico’s vroeg; beloof geen onbewezen oplossing. |
| R05 | Arbeidsvoorwaarden en opleidingsmogelijkheden | Maaltijd/ecocheques, verzekeringen, GSM/laptop, wagen, vergoeding en cafetariaplan worden genoemd. | Vraag voorwaarden, budget en praktische opleidingstijd. |
| R06 | Technische projectplannen beheren en rapporteren | Jij organiseert technische uitvoering en afhankelijkheden. | Maak mijlpalen, eigenaar, risico’s, planning en wekelijkse status. |
| R07 | Externe bedrijven aansturen | Uitbesteden verwijdert je verantwoordelijkheid voor resultaat niet. | Specificeer deliverables, acceptatie, deadlines en escalaties. |
| R08 | Core-systemen en nieuw Terminal Systeem | Continuïteit van huidige applicaties naast verandering. | Leg datastromen vast; plan migratie, test en herstel. |
| R09 | Kwaliteit, veiligheid en milieu ondersteunen | IT-keuzes hebben operationele gevolgen. | Bespreek foutieve data, toegang, traceerbaarheid en veilige workarounds. |
| R10 | Specificaties toetsen aan strategie/procedures/standaarden | Een technisch haalbare wijziging moet ook passen in afspraken. | Controleer ontwerp, security, lifecycle en changevoorwaarden. |
| R11 | Bijstaan in behoeftenanalyse | Vraag door naar probleem en gebruikersdoel. | Observeer huidige werkwijze; maak acceptatiecriteria. |
| R12 | Lastenboek, werkpakketten en CRQ | CRQ is het change request: waarom, wat, risico en goedkeuring. | Beschrijf scope, interfaces, tests, uren, rollout en rollback. |
| R13 | Implementatie begeleiden | Delivery controleren tot het werkend in gebruik is. | Volg issues en afhankelijkheden; organiseer acceptatie en nazorg. |
| R14 | Gebruikers opleiden | Adoptie is deel van technisch succes. | Maak taakgerichte demo, oefencases en korte werkinstructie. |
| R15 | Outsourcing coördineren | Organiseer de grens tussen interne en externe uitvoering. | Leg eigenaarschap, toegang, overdracht en exitdocumentatie vast. |
| R16 | Capaciteit en budget bewaken | Bewaken of inspanning en resultaat nog kloppen. | Vergelijk forecast/actual, scope en resterend werk; escaleer afwijkingen. |
| R17 | Applicatiecomponenten in kaart brengen/analyseren/evalueren | Ken componenten, afhankelijkheden en kwetsbare punten. | Maak componentcatalogus met eigenaar, versie en interface. |
| R18 | Releases op servers/systemen met partners coördineren | Versies moeten samen compatibel live gaan. | Gebruik releasekalender, compatibiliteitsmatrix en go/no-go. |
| R19 | TOS met IBM P-series, AIX, Oracle en JBoss | Bedrijfskritische applicaties op enterpriseplatformen. | Traceer gebruiker → applicatie → query; stem platformproblemen af. |
| R20 | EDI-processing en rapportering met WebFOCUS/iWay | EDI is gestructureerde gegevensuitwisseling tussen organisaties. | Volg bericht van ontvangst tot businessresultaat; controleer rapportdefinities. |
| R21 | Webportalen opzetten en beheren | Gebruikersinterfaces met lifecycle en toegangsbeheer. | Beheer configuratie, permissies, tests, certificaten en releasebewijs. |
| R22 | Nieuwe functionaliteit en koppelingstools ontwikkelen | Hands-on bouwen maakt deel uit van de functie. | Implementeer kleine wijziging met contract, validatie en logging. |
| R23 | Projectportefeuille beheren | Meerdere projecten concurreren om dezelfde capaciteit. | Orden op impact, afhankelijkheden, risico en beschikbare mensen. |
| R24 | Afwijkingen proactief vinden en bijsturen | Niet wachten op mislukte oplevering. | Vergelijk voortgang met baseline en stel opties met gevolgen voor. |
| R25 | Tweede lijn incident/problem/change tot afronding | Service Desk draagt complexere applicatieproblemen over. | Prioriteer, onderzoek, communiceer, herstel en documenteer oorzaak. |
| R26 | Wekelijks IT en business rapporteren | Vertaal techniek naar voortgang en impact. | Meld resultaat, risico, budget/capaciteit, besluit en volgende stap. |
| R27 | Intern/extern ontwikkelingsteam en training nieuwe collega’s | Technische samenwerking en taakgerichte sturing. | Doe review, overdracht en begeleid een collega met echte oefencase. |
| R28 | IT-evoluties volgen; technische kennis en analyse | Maak passende verbeterkeuzes, geen technologie om zichzelf. | Vergelijk lifecycle, kosten en operationele haalbaarheid. |
| R29 | PRINCE2 of andere projectmethode | Methodisch plannen, beslissen en risico’s beheersen. | Gebruik businesscase, fasering en tolerantie; certificaat niet expliciet vereist. |
| R30 | MS Office en gerelateerde producten | Praktische analyse, rapportage en communicatie. | Gebruik Excel voor reconciliatie, Word voor CRQ, presentatie voor opleiding. |
| R31 | Apex | Waarschijnlijk Oracle APEX gezien Oracle-stack; verifiëren. | Oefen formulieren, SQL-rapporten, validatie en rechten. |
| R32 | Talen N/E/F | Waarschijnlijk Nederlands/Engels/Frans; niveau onbekend. | Leg incident uit, lees documentatie en voer leveranciersoverleg. |
| R33 | Communiceren, organiseren, stress en taakgericht leidinggeven | Techniek en mensen onder druk op één resultaat richten. | Prioriteer transparant; benoem eigenaar en updatefrequentie. |
| R34 | Supervisor/Director IT; projectcoördinator/business/klanten/leveranciers | Beslissen gebeurt in een netwerk van stakeholders. | Maak beslisrechten, escalatie en communicatie per doelgroep duidelijk. |
| R35 | Applicatieomgevingen Kallo én Zeebrugge | Wijzigingen kunnen meerdere locaties raken. | Test locatieconfiguratie en operationele afhankelijkheden per site. |
