# Proposed system architecture — Terminal Flow Control

**Assumption / realistic simulation.** Vacature noemt TOS, AIX/IBM P-series, Oracle, JBoss, EDI, iWay, WebFOCUS, portalen en Apex; onderstaande topology is fictief. Dit is geen reconstructie van een vertrouwelijke ICO-omgeving.

## Centrale case

Partners sturen voertuig-aankomst, verplaatsing en vertrek voor twee sites. Operations ziet actuele locatie/status, kan gecontroleerd corrigeren en een hold laten beheren. Het systeem journaliseert ontvangst, verwerkt met businessregels en verstuurt na commit een afzonderlijke bevestiging. Reporting telt unieke actieve voertuigen met vaste site/partnerdefinitie. De medewerker onderzoekt backlog, afwijzingen, dubbele verzendingen, statusconflicten en release-effecten.

## System context

```mermaid
flowchart LR
  Partner[Partner ALPHA / BETA simulator] -->|Bearer JSON-profiel| OS[Terminal Flow Control]
  Operator[Operations / business] -->|Taakgericht portaal| OS
  IT[Development officer / tweede lijn] -->|Diagnose, controls, releases| OS
  OS -->|Ondertekend ACK na commit| ACK[Lokale partner ACK-server]
  OS -->|SQL / CSV| Reports[Rapportering / weekrapport]
```

## Component diagram

```mermaid
flowchart TD
  UI[HTML/JS portaal] --> Router[Router + role/scope + request limits]
  Partner[Inbound API] --> Router
  Router --> Service[TerminalService: validatie / acceptatie / correcties]
  Service --> DB[(H2 JDBC: message journal, voertuigen, audit)]
  Worker[Worker: mapping / business transitions] --> DB
  Worker --> Outbox[ACK dispatcher: bounded retry / HMAC]
  Outbox --> Callback[Partner callback HTTP simulator]
  Router --> Metrics[Metrics / health / rapportdefinities]
  DB --> Metrics
```

## Data flow

```mermaid
sequenceDiagram
  participant P as Partner
  participant A as API
  participant D as Database
  participant W as Worker
  participant C as ACK endpoint
  P->>A: Event + business event_key + bearer
  A->>D: Atomische ontvangst / unieke partner-eventkey
  A-->>P: 202 RECEIVED (geen businessbevestiging)
  W->>D: Validatie, transition, vehicle + audit + outbox commit
  W->>C: HMAC-signed ACK
  C-->>W: 200 receipt
  W->>D: ACK-status SENT
  Note over D,C: Timeout na commit: ACK retry, geen dubbele vehicle mutation
```

## Integration flow

```mermaid
stateDiagram-v2
  [*] --> RECEIVED
  RECEIVED --> PROCESSED: business commit
  RECEIVED --> REJECTED: permanent contract/businessfout
  RECEIVED --> RETRY_WAIT: tijdelijke dependencyfout
  RETRY_WAIT --> PROCESSED: herstel + veilige retry
  RETRY_WAIT --> DEAD_LETTER: attemptlimiet
  PROCESSED --> ACK_PENDING
  ACK_PENDING --> ACK_SENT: bevestiging ontvangen
  ACK_PENDING --> ACK_RETRY_WAIT: timeout / 5xx
  ACK_RETRY_WAIT --> ACK_SENT: opnieuw dezelfde eventbevestiging
  ACK_RETRY_WAIT --> ACK_DEAD_LETTER: attemptlimiet
```

## Deployment architecture

```mermaid
flowchart LR
  Git[Git change + CRQ] --> Tests[JUnit + HTTP acceptance + SQL checks]
  Tests --> WAR[Versioned WAR + SHA256 manifest]
  WAR --> Review[Test/UAT + simulated approval]
  Review --> WF[WildFly standalone localhost lab]
  WF --> Database[(Afzonderlijke file DB per omgeving)]
  WF --> Partner[Lokale ACK simulator]
  WF --> Verify[Health + business smoke + audit + reconciliation]
```

Local fast path gebruikt JDK HttpServer met dezelfde router/domaincode. WAR heeft een echte Jakarta Servlet-adapter. De Servlet-container beheert init/destroy en start/stopt de worker. De local adapter is geen JBoss-vervanger; de WAR-test moet apart aantonen dat containerdeployment werkt.

## Grenzen en eigenaarschap

Eén monolith, één database, één actieve workerinstance: geen Kafka, Kubernetes, gedistribueerde locking of microservices. Local HTTP alleen op loopback; productionlike TLS, identityprovider, enterprise JDBC-pool en AIX moeten afzonderlijk ontworpen/gevalideerd worden. Authenticator gebruikt lokaal gegenereerde tokens en rol/site/partner-scope. Transportreceipt, businesscommit en ACK worden apart gelogd. Externe communicatie is fictief en wordt niet werkelijk naar ICO of leveranciers verzonden.

DB-atomiciteit bewaakt voertuig/audit/outbox. Callback kan duplicaat-ACK ontvangen: event-ID is stabiel en callback is idempotent. Slechts transient fouten worden automatisch opnieuw geprobeerd; malformed en ongeldige transitions blijven verklaarbaar afgewezen. Re-drive is bevoegd, gelogd en beperkt tot failed messages zonder reeds verwerkt event.
