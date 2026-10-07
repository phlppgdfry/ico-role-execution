# Functional specification

| ID | User story / rule | Edge cases |
|---|---|---|
| FR01 | Als partner stuur ik event met mijn site/partner-scope | Spoofing 403; syntax/unknown keys 400; 16 KiB limit 413 |
| FR02 | Als partner krijg ik receipt-ID en status | New 202; same business payload 200 duplicate; changed payload 409 |
| FR03 | Als operations volg ik durable journal | RECEIVED/RETRY_WAIT/PROCESSED/REJECTED/DEAD_LETTER zichtbaar |
| FR04 | Worker past geldige transitions atomisch toe | Invalid site/location, old version/time, ownership of hold blokkeren |
| FR05 | Callback krijgt pas na commit HMAC-ACK | Timeout retry zonder businessreplay; permanente 4xx naar dead letter |
| FR06 | Operator corrigeert locatie | Reader 403; invalid site 400; old version 409; reason verplicht |
| FR07 | Operator legt hold vast; approver geeft vrij | Release ADMIN + decision_ref; versiecheck/audit; geen fysieke claim |
| FR08 | Admin wijzigt labcontrols/re-drives | Alleen gelabelde sandbox; processed message nooit re-drive |
| FR09 | Reader/partner krijgt correct scoped report | Count vehicles, not deliveries; two sites and partner-scope |
| FR10 | Tweede lijn diagnosticeert read-only | Query-name whitelist, no arbitrary SQL, admin only |
| FR11 | Release owner bouwt en valideert WAR | Hash/version, config/secrets apart, rollbackcompatibiliteit |

Reception, domaincommit and callbackdelivery zijn aparte fasen. Een fout in ACK mag geen vehiclemutatie ongedaan maken. Portaalfeedback houdt token in geheugen, toont fouten en gebruikt dezelfde serverautorisatie als direct API-verkeer.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.
