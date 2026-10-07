# Synthetic EDI profile

The actual ICO EDI standard/transport is unknown. This JSON contract demonstrates EDI concepts, not EDIFACT compliance. All nine fields are required; extra fields rejected. message_id is transport identity, event_key is partner-specific business identity. A retry may change message_id while preserving the business payload. Changed payload under the same event_key returns 409. IDs are bounded; synthetic vin is 17 uppercase alphanumerics, not an official VIN/checkdigit implementation.

event_at must parse as ISO instant and be at most five minutes in the future. expected_version is integer ≥0. Initial ARRIVAL requires 0; transitions require current version and increasing event time. MOVE/DEPARTURE require active vehicle, same site/partner and active masterdata location. DEPARTURE blocked by hold and requires current location. Re-arrival is allowed only for departed vehicle with current expected version and later timestamp. Business rejects are asynchronous and visible in journal, not automatically retried.

Mapping v1 requires exact location code. v2 supports only the two prefixes represented by reviewed examples, then checks masterdata again. No catch-all location or silent coercion. Arrival/move/departure samples form one ordered demo; unknown-location uses a separate vehicle. Repeating the same arrival returns duplicate receipt rather than creates another vehicle.

---
**Assumption / realistic simulation.** Fictieve terminal, rollen, tijdlijnen en beslissingen; geen ICO-feiten, dienstverband of werkelijk verzonden communicatie. Werkelijk testbewijs staat afzonderlijk in `docs/testing/verification.md`.

