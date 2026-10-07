# Hiring manager guide — vijf minuten

Dit is een **Job Execution Repository / Role Operating System** voor de ICO IT Development Officer-vacature. Alle operationele rollen, historische tickets/incidenten/approvals en businesscase zijn **Assumption / realistic simulation**. Werkelijke uitvoerbaarheid wordt bewezen door broncode, tests en afzonderlijk geregistreerde testresultaten. Geen dienstverband/diploma/productexperience verzonnen.

## Snelle route

1. Bekijk requirements→proof hieronder: verantwoordelijkheid in plaats van random frameworks.
2. Start de verticale flow en herhaal een event: één business-effect, duidelijke journal/ACK.
3. Lees INC006/CHG001: waarom ACKtimeout niet dezelfde herstelactie is als mislukte commit.
4. Bekijk locatiecorrectie: rol,scope,version,reason,audit en holdbusinessdecision.
5. Bekijk werkelijk WAR/recovery/testbewijs en grenzen van H2/AIX/iWay/WebFOCUS/APEX-substituties.

| Vacaturevereiste | Concrete demonstratie / artefact | Bewijsgrens |
|---|---|---|
| R01 — Permanente functie, Zeebrugge, 38 uur | [docs/role/role-operating-manual.md](../docs/role/role-operating-manual.md) | context / review |
| R02 — IT-master of bachelor gelijkgesteld door ervaring | [docs/role/vacancy-analysis.md](../docs/role/vacancy-analysis.md) | context / review |
| R03 — Dagshift, beperkte verplaatsingen en wachtdienst | [docs/runbooks/on-call-handover.md](../docs/runbooks/on-call-handover.md) | execution / simulation |
| R04 — Integriteit, intensiteit, innovatie | [docs/role/top-performer-guide.md](../docs/role/top-performer-guide.md) | execution / simulation |
| R05 — Arbeidsvoorwaarden en opleidingsmogelijkheden | [docs/onboarding/30-60-90-day-plan.md](../docs/onboarding/30-60-90-day-plan.md) | context / review |
| R06 — Technische projectplannen beheren en rapporteren | [docs/requirements/project-plan.md](../docs/requirements/project-plan.md) | execution / simulation |
| R07 — Externe bedrijven aansturen | [docs/stakeholders/vendor-work-package.md](../docs/stakeholders/vendor-work-package.md) | execution / simulation |
| R08 — Core-systemen en nieuw Terminal Systeem | [docs/releases/cutover-rehearsal.md](../docs/releases/cutover-rehearsal.md) | execution / simulation |
| R09 — Kwaliteit, veiligheid en milieu ondersteunen | [docs/security/safety-quality-environment.md](../docs/security/safety-quality-environment.md) | execution / simulation |
| R10 — Specificaties toetsen aan strategie/procedures/standaarden | [docs/architecture/decisions.md](../docs/architecture/decisions.md) | execution / simulation |
| R11 — Bijstaan in behoeftenanalyse | [docs/requirements/business-requirements.md](../docs/requirements/business-requirements.md) | execution / simulation |
| R12 — Lastenboek, werkpakketten en CRQ | [docs/changes/CHG-001-retry-and-replay.md](../docs/changes/CHG-001-retry-and-replay.md) | execution / simulation |
| R13 — Implementatie begeleiden | [deployment/deployment-runbook.md](../deployment/deployment-runbook.md) | execution / simulation |
| R14 — Gebruikers opleiden | [docs/onboarding/user-training.md](../docs/onboarding/user-training.md) | execution / simulation |
| R15 — Outsourcing coördineren | [docs/stakeholders/vendor-work-package.md](../docs/stakeholders/vendor-work-package.md) | execution / simulation |
| R16 — Capaciteit en budget bewaken | [operations/portfolio/capacity-budget.csv](../operations/portfolio/capacity-budget.csv) | execution / simulation |
| R17 — Applicatiecomponenten in kaart brengen/analyseren/evalueren | [docs/architecture/component-catalogue.md](../docs/architecture/component-catalogue.md) | execution / simulation |
| R18 — Releases op servers/systemen met partners coördineren | [docs/releases/REL-1.4.0.md](../docs/releases/REL-1.4.0.md) | execution / simulation |
| R19 — TOS met IBM P-series, AIX, Oracle en JBoss | [docs/systems/platform-substitutions.md](../docs/systems/platform-substitutions.md) | execution / simulation |
| R20 — EDI-processing en rapportering met WebFOCUS/iWay | [docs/integrations/partner-contract.md](../docs/integrations/partner-contract.md) | execution / simulation |
| R21 — Webportalen opzetten en beheren | [src/main/webapp/index.html](../src/main/webapp/index.html) | execution / simulation |
| R22 — Nieuwe functionaliteit en koppelingstools ontwikkelen | [src/main/java/roleos/TerminalService.java](../src/main/java/roleos/TerminalService.java) | execution / simulation |
| R23 — Projectportefeuille beheren | [operations/portfolio/project-portfolio.csv](../operations/portfolio/project-portfolio.csv) | execution / simulation |
| R24 — Afwijkingen proactief vinden en bijsturen | [docs/stakeholders/weekly-report.md](../docs/stakeholders/weekly-report.md) | execution / simulation |
| R25 — Tweede lijn incident/problem/change tot afronding | [docs/incidents/INC-001-worker-stalled.md](../docs/incidents/INC-001-worker-stalled.md) | execution / simulation |
| R26 — Wekelijks IT en business rapporteren | [docs/stakeholders/weekly-report.md](../docs/stakeholders/weekly-report.md) | execution / simulation |
| R27 — Intern/extern ontwikkelingsteam en training nieuwe collega’s | [docs/onboarding/buddy-plan.md](../docs/onboarding/buddy-plan.md) | execution / simulation |
| R28 — IT-evoluties volgen; technische kennis en analyse | [docs/architecture/lifecycle-review.md](../docs/architecture/lifecycle-review.md) | execution / simulation |
| R29 — PRINCE2 of andere projectmethode | [docs/requirements/project-plan.md](../docs/requirements/project-plan.md) | execution / simulation |
| R30 — MS Office en gerelateerde producten | [operations/portfolio/capacity-budget.csv](../operations/portfolio/capacity-budget.csv) | execution / simulation |
| R31 — Apex | [docs/systems/apex-porting-plan.md](../docs/systems/apex-porting-plan.md) | execution / simulation |
| R32 — Talen N/E/F | [docs/stakeholders/multilingual-updates.md](../docs/stakeholders/multilingual-updates.md) | execution / simulation |
| R33 — Communiceren, organiseren, stress en taakgericht leidinggeven | [docs/role/role-operating-manual.md](../docs/role/role-operating-manual.md) | execution / simulation |
| R34 — Supervisor/Director IT; projectcoördinator/business/klanten/leveranciers | [docs/stakeholders/raci.md](../docs/stakeholders/raci.md) | execution / simulation |
| R35 — Applicatieomgevingen Kallo én Zeebrugge | [tests/acceptance/test_live_api.py](../tests/acceptance/test_live_api.py) | execution / simulation |

## Wat ik wel en niet aantoon

Wel: requirements, SQL/transaction/integration/security boundaries, concrete troubleshooting/control/report/release/recovery and stakeholderartefacts. Werkend Java/JDBC/HTTP/WAR-lab, meetbare negative/concurrency tests. Niet: echte Oracle/AIX/iWay/WebFOCUS/APEX-administratie, ICO-internalarchitecture, professionalexperience, taalniveau/diploma, availability or actualbudgetmandate. Ask candidate to demonstrate and explain own contribution; repository alone proves no unaidedmastery.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
