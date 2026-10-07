# Actual verification evidence

Dit document registreert werkelijk uitgevoerde tests, niet fictieve operationele historie. Synthetische data; geen credentials of interne ICO-systemen.

UTC: 2026-10-07T00:31:45.667589+00:00

WAR SHA256: `05accc3edf1512424ceb0b1a1e30ddd4587b202e62147f9336834632857dbb7d`

| Check | Tests/checks | Exit | Resultaat |
|---|---:|---:|---|
| Java domain/concurrency/database/security | 25 | 0 | PASS |
| HTTP fast local | 7 | 0 | PASS |
| HTTP actual WildFly WAR | 7 | 0 | PASS |
| Migration/restore/cutover | 3 | 0 | PASS |
| Operational automations | 7 | 0 | PASS |
| Browser task/mobile | 2 | 0 | PASS |
| Vacancy/doc links/spec/schema/known-secret audit | structural | 0 | PASS |

Actual WildFly EE10 41.0.1 WARdeployment + undeploy/redeploy was executed locally; official distribution SHA256 verified. Same HTTPcontract exercised in both adapters. Migrationbackup/restorefresh-target and bad/goodcutover tested. Browser/IAB unavailable, PlaywrightChromium fallback; desktop and390pxmobile, actual state and negative authorization.

[Desktop portal](portal-desktop.png) · [Mobile portal](portal-mobile.png) · [Machine-readable evidence](../../operations/evidence/verification.json). Screenshots contain masked generatedtoken,syntheticdata only.

Limits: no actualOracle/AIX/iWay/WebFOCUS/APEX runtime,productionTLS/identity/HA/load,Safari/Firefox/pentest. No SLA/readiness/personalsuitabilitygrade. Actual context and authority must be established onjob.

## GitHub verification

[Default CI](https://github.com/phlppgdfry/ico-role-execution/actions/runs/37552644079) completed successfully. [Full actual WildFly/WAR/lifecycle CI](https://github.com/phlppgdfry/ico-role-execution/actions/runs/37552862580) also completed successfully on Ubuntu with Java21. Local Java source was then consistently formatted and recompiled:25 tests,0failures/0errors. This formatting changes no business behaviour.
