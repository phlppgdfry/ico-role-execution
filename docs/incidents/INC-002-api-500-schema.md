# INC-002 — API geeft HTTP 500 na ongeldige schemawijziging

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV2; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-15 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Voertuiglijst niet beschikbaar in test; productieachtige beslissingen uitsluitend geautoriseerd.

## Affected systems

Router, JDBC, schema

## Symptoms

500 INTERNAL_ERROR met correlation; SQLdetails niet naar gebruiker gelekt.

## Hypotheses / counterevidence

H1 tabel/schema ontbreekt; H2 authfout; H3 netwerk. 500 ná auth en requestlog weerspreekt 401/netwerk als eerste grens.

## Investigation

Runtime/config/artefact en schema_version vergelijken. Gereproduceerd in verse unit DB door vehicles te verwijderen, nooit in actieve main lab. Query faalt, router logt exception_class maar geen raw SQL/secret.

## Logs

request.internal_error, exception_class=IllegalStateException; request.completed 500. Root DB-exception alleen via bevoegde technische debug in test.

## Database checks

Schema_version/information_schema via DBA; gewone query inventory. Geen CREATE/restore onder live users zonder herstelbesluit.

## Root cause in this scenario

Scenario: foutieve migrationtarget verwijderd tabel die app verwachtte; codeversie en databasestate niet compatibel.

## Workaround

Stop releaseprogress, registreer current state en schakel veilige vorige testtarget in als bewezen compatible.

## Permanent fix

Fresh-target restore of reviewed forward migration; predeploy schema gate en regression op ontbrekende dependency.

## Validation / evidence boundary

routerInternalErrorSuppressesSqlDetails + WAR schema/query acceptance; geen ongefundeerde app-only rollback.

## Communication

“Testrelease heeft schema-afhankelijkheidsfout. We houden livegang tegen. Data-/schemastatus wordt eerst vastgesteld; daarna bevoegd herstelbesluit.”

## Lessons learned

500 is symptoom; eerste oorzaak ligt in deploy/schema, niet automatisch appcode.

## Lab reproduction

JUnit routerInternalErrorSuppressesSqlDetails uses isolated memory DB only

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
