CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at BIGINT NOT NULL);
CREATE TABLE IF NOT EXISTS sites (site_id VARCHAR(8) PRIMARY KEY, site_name VARCHAR(80) NOT NULL);
CREATE TABLE IF NOT EXISTS partners (partner_id VARCHAR(16) PRIMARY KEY, partner_name VARCHAR(80) NOT NULL);
CREATE TABLE IF NOT EXISTS locations (location_id VARCHAR(32) PRIMARY KEY, site_id VARCHAR(8) NOT NULL REFERENCES sites(site_id), active BOOLEAN NOT NULL);
CREATE TABLE IF NOT EXISTS messages (
 id VARCHAR(36) PRIMARY KEY, partner_id VARCHAR(16) NOT NULL REFERENCES partners(partner_id),
 event_key VARCHAR(64) NOT NULL, transport_id VARCHAR(64) NOT NULL, site_id VARCHAR(8) NOT NULL REFERENCES sites(site_id),
 vin VARCHAR(17) NOT NULL, payload CLOB NOT NULL, payload_hash VARCHAR(64) NOT NULL,
 status VARCHAR(20) NOT NULL CHECK (status IN ('RECEIVED','RETRY_WAIT','PROCESSED','REJECTED','DEAD_LETTER')),
 attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts>=0), received_at BIGINT NOT NULL, processed_at BIGINT,
 next_attempt_at BIGINT NOT NULL DEFAULT 0, last_error VARCHAR(64),
 UNIQUE(partner_id,event_key)
);
CREATE INDEX IF NOT EXISTS idx_messages_ready ON messages(status,next_attempt_at,received_at);
CREATE INDEX IF NOT EXISTS idx_messages_scope ON messages(partner_id,site_id,received_at);
CREATE TABLE IF NOT EXISTS deliveries (id VARCHAR(36) PRIMARY KEY, message_id VARCHAR(36) NOT NULL REFERENCES messages(id), transport_id VARCHAR(64) NOT NULL, duplicate BOOLEAN NOT NULL, received_at BIGINT NOT NULL);
CREATE TABLE IF NOT EXISTS vehicles (
 vin VARCHAR(17) PRIMARY KEY, partner_id VARCHAR(16) NOT NULL REFERENCES partners(partner_id), site_id VARCHAR(8) NOT NULL REFERENCES sites(site_id),
 location_id VARCHAR(32) NOT NULL REFERENCES locations(location_id), state VARCHAR(12) NOT NULL CHECK (state IN ('ACTIVE','DEPARTED')),
 hold_flag BOOLEAN NOT NULL DEFAULT FALSE, version INTEGER NOT NULL CHECK (version>0), last_event_at BIGINT NOT NULL, updated_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vehicles_report ON vehicles(site_id,state,partner_id);
CREATE TABLE IF NOT EXISTS business_events (id VARCHAR(36) PRIMARY KEY, message_id VARCHAR(36) UNIQUE REFERENCES messages(id), vin VARCHAR(17) NOT NULL REFERENCES vehicles(vin), event_type VARCHAR(32) NOT NULL, event_at BIGINT NOT NULL, applied_at BIGINT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_log (id VARCHAR(36) PRIMARY KEY, actor VARCHAR(32) NOT NULL, action VARCHAR(40) NOT NULL, entity_id VARCHAR(64) NOT NULL, before_value VARCHAR(240), after_value VARCHAR(240), reason VARCHAR(240) NOT NULL, correlation_id VARCHAR(64) NOT NULL, created_at BIGINT NOT NULL);
CREATE TABLE IF NOT EXISTS outbox (
 id VARCHAR(36) PRIMARY KEY, message_id VARCHAR(36) NOT NULL UNIQUE REFERENCES messages(id), payload CLOB NOT NULL,
 status VARCHAR(20) NOT NULL CHECK(status IN ('PENDING','RETRY_WAIT','SENT','DEAD_LETTER')),
 attempts INTEGER NOT NULL DEFAULT 0, next_attempt_at BIGINT NOT NULL DEFAULT 0, last_error VARCHAR(64), created_at BIGINT NOT NULL, sent_at BIGINT
);
CREATE INDEX IF NOT EXISTS idx_outbox_ready ON outbox(status,next_attempt_at,created_at);
CREATE TABLE IF NOT EXISTS controls (control_name VARCHAR(40) PRIMARY KEY, control_value VARCHAR(40) NOT NULL);
MERGE INTO sites KEY(site_id) VALUES ('ZEE','Zeebrugge simulation'),('KAL','Kallo simulation');
MERGE INTO partners KEY(partner_id) VALUES ('ALPHA','Synthetic partner ALPHA'),('BETA','Synthetic partner BETA');
MERGE INTO locations KEY(location_id) VALUES ('ZEE-A01','ZEE',TRUE),('ZEE-A02','ZEE',TRUE),('KAL-B01','KAL',TRUE),('KAL-B02','KAL',TRUE);
INSERT INTO schema_version(version,applied_at) SELECT 1,0 WHERE NOT EXISTS (SELECT 1 FROM schema_version WHERE version=1);
