# INC-005 — Nieuwe partnerlocatiecode wordt afgewezen

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV2; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-18 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Afgebakende ALPHA-codevariant; andere geldige locaties blijven verwerken.

## Affected systems

Mapping, masterdata, journal, worker

## Symptoms

REJECTED / UNKNOWN_LOCATION for ZEE-A-01; receipt exists, no vehicle mutation.

## Hypotheses / counterevidence

H1 agreed alias missing; H2 genuine invalid location; H3 wrong site. Vraag businesscatalog/partnercontractbewijs.

## Investigation

Compare exact input code with active site masterdata and mapping version. v1 exact check rejects. v2 normalises only reviewed prefix then revalidates. No fictitious fallback location.

## Logs

message.rejected error_code UNKNOWN_LOCATION; controls/redrive audit records change and owner.

## Database checks

failed-messages; check locations site/active; reconciliation empty before/after.

## Root cause in this scenario

Scenario: approved partner alias absent in v1; contractchange was not coordinated with mappingdelivery.

## Workaround

Reject expliciet houden, partner originele agreed code laten sturen indien toegestaan; geen silent statusforce.

## Permanent fix

CHG-003 mapping2 + site-negative tests + admin reasoned redrive of affected unprocessed IDs only.

## Validation / evidence boundary

mappingFixAndAuthorizedRedriveAreAudited + HTTP03; processed redrive returns409; exactly one event/outbox.

## Communication

“Alleen codevariant ZEE-A-01 wordt geweigerd; bericht is bewaard. Partner/operations bevestigen de code, daarna beperkte mappingchange en gecontroleerde herverwerking.”

## Lessons learned

Mappingrelease is contractchange; both sites and invalid codes test.

## Lab reproduction

edi/samples/unknown-location.json; mapping2; redrive receipt

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
