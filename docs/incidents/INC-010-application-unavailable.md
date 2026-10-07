# INC-010 — Applicatiepad unavailable met gecontroleerde recovery

**Recordstatus:** RESOLVED (fictieve scenariohistorie). **Severity:** SEV2; interne prioriteit bij ICO onbekend. **Timestamp/timeline:** 2026-09-23 08:30 UTC detectie; 08:35 scope/owner; 08:45 hypothesetoets; 09:05 herstelbesluit; 09:20 validation; 10:00 overdracht. Alle tijden zijn fictief.

## Business impact

Portal/API-taken tijdelijk geblokkeerd; queue/data blijven durable.

## Affected systems

API readiness, portal, control/audit

## Symptoms

503 health DEGRADED and API failure under explicit lab control; admin controls recovery remains reachable.

## Hypotheses / counterevidence

H1 intentional faultflag; H2 DB unreachable; H3 container down; H4 route failure. If no HTTP connection, control path cannot fix runtime.

## Investigation

Check healthresponse versus connectionrefused; app/servletprocess and currentcontrolaudit; confirm timestamps/siteimpact. Lab force_api_failure proves503 handling, not physical networkoutage.

## Logs

request.completed503; controls LAB_CONTROL old/new; runtime/container log for genuinely absent process.

## Database checks

Read-only diagnostics after recovery, reconciliation and outbox-state; never delete inputqueue.

## Root cause in this scenario

Scenario: faultflag enabled for readiness rehearsal; handover did not state current availabilitymode.

## Workaround

Businessowner stops affected demo tasks; preserve state and updates. Real runtimeabsence escalate to platformowner.

## Permanent fix

Admin clears explicit lab flag, health/true business smoke/reconciliation; improve critical-event/end-trainingcheck.

## Validation / evidence boundary

HTTP06 + smoke both sites; no empty greencheck without businessflow.

## Communication

“Applicatiepad is tijdelijk niet beschikbaar. Data blijft bewaard; we herstellen de gecontroleerde toestand en testen daarna beide sites end-to-end.”

## Lessons learned

Know when recovery is app config versus OS/container; do not blanket restart.

## Lab reproduction

force_api_failure true; health503; admin reset; business-smoke

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
