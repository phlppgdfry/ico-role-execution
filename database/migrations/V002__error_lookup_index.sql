CREATE INDEX IF NOT EXISTS idx_messages_error ON messages(status,received_at,last_error);
INSERT INTO schema_version(version,applied_at) SELECT 2,0 WHERE NOT EXISTS (SELECT 1 FROM schema_version WHERE version=2);
