# Stakeholders / RACI — fictieve rolverdeling

R executes, A owns/decides, C consulted, I informed. Real ICO mandaat must be confirmed. Vacancy reports Supervisor/Director and contacts internal/external team,projectcoordinator,business,customers/vendors/Service Desk; separate runtime/data/security roles are assumptions.

| Activity | R | A | C / I |
|---|---|---|---|
| Incidenttriage/businessimpact | Service Desk/officer | Incidentowner | Keyuser/runtime/data/vendor; businessupdated |
| Permanent technicalfix | Developer/integrationpartner | IT supervisor | Officer/test/business |
| Physical hold/release rule | Businessoperations | Businessapprover | IT implements/audits, not autonomous release |
| Data/schema/recovery | Dataowner | Authorized IT/dataowner | Runtime/officer/business |
| Vendorworkpackage/acceptance | Officer | Supervisor/budgetowner | Projectcoordinator/keyuser/vendor |
| Release go/no-go | Releaseowner/officer | Supervisor + businessowner | Runtime/data/vendor/Service Desk |
| Reportdefinition | Businessdataowner | Businessunitowner | Officer/reportdeveloper |
| Securitycontainment | Security/runtimeowner | Securitylead | Officer/management; controlled externalcomms |

One incidentowner, one actionowner per follow-up, no responsibility without decisionrights. Externalupdates use approved channel; repo samples never actually sent.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
