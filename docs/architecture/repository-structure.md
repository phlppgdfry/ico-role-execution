# Repository structure — vóór implementatie vastgesteld

**Assumption / realistic simulation.** Alleen directories met betekenisvolle inhoud. Java volgt Maven-layout zodat WAR tooling werkt; scripts zijn onder src/scripts, niet verspreid als losse snippets.

```text
README.md / pom.xml / Makefile
docs/
  role/              vacature, drie matrices, operating manual, top performer
  architecture/      vijf diagrammen, componentcatalogus, ADR, lifecycle
  requirements/      BR/FR/tech/NFR/acceptance/projectplan
  systems/           expliciete productsubstituties en APEX-overdracht
  integrations/      partnercontract, retries, ACK en mapping
  runbooks/          tien foutdomeinen en wachtdienstoverdracht
  incidents/         tien uitgewerkte incidentrecords, met evidencegrens
  problems/          drie RCA/5-Whys met structurele acties
  changes/           drie CRQ’s met implementatie/test/recovery
  releases/          release 1.4.0 en cutoverrehearsal
  security/          baseline, review en fysieke safety-impact
  monitoring/        metricdefinities en logging/alerts
  testing/           teststrategie en traceability
  stakeholders/      RACI, vendorwerkpakket, NL/EN/FR, rapportage
  onboarding/        30/60/90, buddy en taakgerichte training
src/main/java/roleos/ router, auth, DB, domein, worker, local en servlet adapter
src/main/resources/  canonieke schema/migrations/mapping
src/main/webapp/     portaal, web.xml, stylesheet, browsercode
src/test/java/       unit/DB/domain/concurrency-tests
src/scripts/         CLI, mockpartner, diagnostics, audit/rehearsal
database/            schema, migrations, diagnostics, reporting/quality queries
api/                 OpenAPI, request/responsevoorbeelden en API-tests
edi/                 synthetisch contractprofiel, fixtures en troubleshooting
monitoring/          dashboarddefinitie, alerts en queryverwijzingen
deployment/          environments, runbooks, checks, scripts, rollbackplan
operations/          20 tickets, instance-evidence, portefeuille/capaciteit
tests/               HTTP acceptance en link/documentation audit
.github/             CI, issue- en PR-templates
runtime/             lokaal gegenereerde DB/log/secrets/evidence; gitignored
```

Artefacts zijn aan R01–R35 gekoppeld. Operatiegeschiedenis krijgt expliciet fictieve timestamps/statussen; testresultaten worden afzonderlijk als daadwerkelijk uitgevoerd opgeslagen. Zo wordt een overtuigend werkmodel geen verzonnen professionele ervaring.
