# Lifecycle review / IT evolutions

Observed 7 October 2026: official WildFly downloads offer 41.0.1 and a separate EE10 distribution. The lab uses EE10 so Servlet6 WAR semantics remain controlled; no assumption that ICO uses this release. Dependencies pinned to verified Maven metadata: H2 2.5.252, Jackson2 2.22.3, JUnit6 6.1.3, compiler3.16 (stable instead of beta4).

Review questions: support horizon/security patches, Oracle/JBoss/AIX compatibility, productlicensing, vendor constraints, data migration, team skills, test environment and total ownership cost. A modern release is not automatic business justification. Proposed decision: keep current working vertical flow, establish product/version inventory with runtime owner, assess required Oracle/JBoss product port through impact/test/rollback workpackage. No unnecessary cloud/containerplatform.

Sources: [WildFly downloads](https://www.wildfly.org/downloads/), [WildFly guide](https://docs.wildfly.org/39/Getting_Started_Guide.html), [H2 features](https://h2database.com/html/features.html), [Jakarta servlet lifecycle](https://github.com/eclipse-ee4j/jakartaee-tutorial/blob/master/src/main/asciidoc/servlets/servlets002.adoc). Context7 resolved WildFly only to Elytron (unsuitable), then Jakarta EE tutorial was fetched. No Elytron-specific auth implementation inferred.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
