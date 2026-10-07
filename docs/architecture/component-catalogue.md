# Application modelling / component catalogue

| Component | Owner / purpose | Input/output | Failure / dependency | Version / evidence |
|---|---|---|---|---|
| Inbound API/router | Officer/app team | Bearer event → receipt/error | Auth/rate/shape and DB availability | App 1.4.0, OpenAPI, HTTP tests |
| TerminalService | App team | Validated event → atomic state/audit | Masterdata/version/hold/transaction | Source + JUnit |
| Durable journal | Data owner | Original payload/hash/status | Disk/locks/integrity | H2 schema1 + additive2 |
| Worker/mapping | Integration partner | Pending → processed/reject/retry | Current mapping/dependency control | mapping1/2 + fixtures |
| Outbox/dispatcher | Integration team | Committed event → signed ACK | Callback/TLS production port/retry | HMAC + timeout test |
| ACK simulator | External partner role | HMAC payload → idempotent receipt | Availability/secret | Python mock, loopback |
| Portal | Business key user/app team | Role task → audited correction | API availability/version | HTML/JS, HTTP/UI acceptance |
| Reporting | Business data owner | Vehicles → grouped SQL/CSV | Wrong definition/snapshot | Occupancy query/reconciliation |
| Runtime | Runtime owner | WAR/config → running servlet | Java/container/lifecycle | WildFly EE10 lab + local adapter |
| Controls | Lab approver | Scoped config/fault → audit | Not production mechanism | Admin-only endpoints |

Each release changes the manifest, not just the WAR. Review compatibility between schema, mapping, portal and partner contract. Server inventory for actual ICO remains unknown. OS/hardware/Oracle/productownership must be validated during onboarding.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
