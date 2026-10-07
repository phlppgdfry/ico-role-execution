# INC-008 — Service account-token geweigerd / scope mismatch

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV3; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-21 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Een partnerstroom of gebruiker geblokkeerd; scope niet breed uitrollen.

## Affected systems

Auth/router, partner/client config

## Symptoms

401 for invalid bearer, 403 for role/site spoof, detail404 outside scope.

## Hypotheses / counterevidence

H1 bad/old token; H2 wrong role; H3 wrong target/site; distinguish401/403 without leaking secrets.

## Investigation

Identify accountrole/configowner, exact route/time, expectedscope and recent credentialchange. Compare working scoped request. No token values in incident or stdout.

## Logs

request.completed 401/403/404 with correlation; no Authorization header logged.

## Database checks

No UPDATE account table; lab identity in env config. Site/partner data read by permitted owner only.

## Root cause in this scenario

Scenario: BETA token used for ALPHA/ZEE request; rolemodel correctly denies.

## Workaround

Use correct authorized service identity through owner, not admin key in partner client.

## Permanent fix

Clientconfig correction and role/scope negative tests; secretrotation should update owners/callback independently.

## Validation / evidence boundary

partnerCannotSpoofScope, router auth test, HTTP02; tokens remain private and no data exposure.

## Communication

“De aanvraag past niet bij de gebruikte identiteit/scope. Wij verifiëren accountconfig met de eigenaar; geef geen token mee in e-mail.”

## Lessons learned

A forbidden request is not automatically an application outage.

## Lab reproduction

HTTP acceptance scoped token tests; no real token fixture committed

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
