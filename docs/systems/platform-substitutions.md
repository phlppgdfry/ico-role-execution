# Product/platform substitution and proof boundary

| Vacancy system | Working lab / concrete artefact | What this proves | What it does not prove |
|---|---|---|---|
| IBM P-series | Platform/OS/app ownership diagram + capacity escalation | Layer boundaries and evidence requirements | Hardware, HMC, LPAR or SAN administration |
| AIX | macOS/Linux local Java + AIX transition checklist | Unix/resource/log concepts | AIX command correctness, root/patch/HA practice |
| Oracle | H2 JDBC/Oracle-mode, schema, queries, constraints | SQL/transactions/reconciliation concepts | Oracle-specific syntax/performance/backup/PLSQL execution |
| JBoss | Real WAR deployed to WildFly EE10 lab | Servlet/lifecycle/deploy/recovery integration | ICO JBoss variant/version/cluster/config |
| iWay | Actual worker/mapping/outbox/HMAC integration | Contract/mapping/retry/ACK and diagnosis | Licensed iWay tooling/adapter administration |
| WebFOCUS | Actual grouped SQL/CSV report and reconciliation | BI definitions, datalineage and testing | WebFOCUS syntax/administration/runtime |
| Apex | Actual audited correction portal + portingplan | Business validation/authorization/task UAT | Oracle APEX installation or imported application |

Linux/macOS is used as local simulation environment; the target vacancy explicitly names AIX on IBM P-series. Do not copy Linux-specific troubleshooting commands into an AIX production runbook without checking the exact version and approved procedures. Find OS/process/disk/permission evidence with platformowner. App/DB fixes do not confer hardware mandaat.

Oracle port checklist: Oracle JDBC service/pool configuration; datatypes (BIGINT/BOOLEAN/CLOB equivalents by version), sequences/identity, MERGE/schema syntax, constraint/index names, locking/order-by/fetch compatibility, prepared params/date handling, EXPLAIN via DBA, backup/restore and migration guards. H2 MERGE KEY and IF NOT EXISTS are not advertised Oracle DDL. Do not run lab schema blindly in Oracle.

Enterprise port checklist: identityprovider/SSO/role mapping, TLS, proper secrets/vendortoegang, retained audit, agreed metrics/SLA, clustered queue ownership, transactional business API boundary and real supportprocedure. Local role token is not enterprise identity.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
