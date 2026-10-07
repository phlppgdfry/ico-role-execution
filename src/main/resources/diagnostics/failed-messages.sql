SELECT id,event_key,site_id,status,attempts,last_error,received_at FROM messages WHERE status IN ('REJECTED','DEAD_LETTER','RETRY_WAIT') ORDER BY received_at DESC FETCH FIRST 200 ROWS ONLY;
