# Deployment runbook

Developer → review/CRQ → Maven build/tests → WAR/hash → testtarget/config → UAT/recovery → approved window → deploy → end-to-end validation → nazorg. WAR bundles webapp classes/resources/dependencies; EAR can bundle multiple enterprise modules, but none needed here. Servlet container is application server; exact ICO JBoss variant unknown.

## Fast local development
`mvn -B -ntp package`, `python3 src/scripts/manage.py init`, `start`, `smoke`. Stop via owned-process `stop`, not global pkill. Local adapter is JDK HttpServer, not fake JBoss. Correct directory/env/ports required. Secrets runtimeonly; portal token manually retrieved locally by owner, never committed.

## Genuine WAR lab
`python3 deployment/scripts/wildfly_lab.py install` downloads official pinned EE10 release and validates SHA256. `start` uses separate DB under runtime/wildfly and loopback HTTP+management ports; deploys actual terminal-flow.war via standalone scanner, confirms .deployed/.failed. `test` runs same HTTP acceptance contract under /terminal-flow. `redeploy` undeploys/loads WAR and checks resource/lifecycle persistence; `stop` uses owned process identity. No Docker dependency; server binary/runtime ignored by Git.

Production deployment method must be confirmed with true runtimeowner; scanner is local simulation, not guaranteed preferred enterprise release method. Environment configuration includes app-role secrets, DB target, callback/HMAC, port and limits. No secretliteral in WAR. Logs: runtime/app.log or server.log plus journal/query/audit; inspect first failure not just final “server started”.

Migration: stop target; reviewed snapshot; DbTool migrate file copied inside runtime; DDL may auto-commit. Never assume data rollback. Validation includes real task/input/commit/callback, not health alone. Stop/no-go on unknown state, data/security/safety defects or absent recoveryowner.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
