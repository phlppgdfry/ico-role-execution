# INC-004 — Deployment start niet met verkeerde credentialconfig

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV2; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-17 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Testomgeving niet gereed voor release; geen users trainen op niet-valide target.

## Affected systems

Application init, WAR/container, secrets/config

## Symptoms

Application refuses missing/short/reused token; container deployment failure or local startup failure.

## Hypotheses / counterevidence

H1 ontbrekende envsecret; H2 incompatible Servlet/runtime; H3 DB filelock. Eerst init-exceptionclass en configkeys zonder values.

## Investigation

Artefact hash en containerlog; checklist required env keys; confirm separate runtime dir and correct credentials owner. Do not print env content. Validate constructor rejects invalid token configuration.

## Logs

Servlet init/config failure names required key but not token; deployment failed marker / containerlog.

## Database checks

Geen DB-query noodzakelijk bij auth-initialisatie vóór DB-open; filelock alleen onderzoeken als init verder komt.

## Root cause in this scenario

Scenario: releaseconfig miste één service token; configuration acceptance niet in deploycheck.

## Workaround

Go-live stoppen; eerdere compatible target houden; correctie alleen via credentialowner.

## Permanent fix

Provide generated distinct credentials securely, redeploy correct environment, config preflight and negative startup test.

## Validation / evidence boundary

configurationRequiresDistinctStrongSecrets; actual WAR health and positive/negative auth HTTP acceptance.

## Communication

“Het WAR is gebouwd, maar testconfig is niet compleet. Geen livegang. Credentials worden via eigenaar aangevuld, zonder ze in ticket of logs te delen.”

## Lessons learned

Build success bewijst geen environment readiness; secrets/config horen in releasemanifest boundary.

## Lab reproduction

Auth constructor test, not replacing main-lab credentials

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
