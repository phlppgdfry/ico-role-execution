SELECT id,event_key,status,last_error,attempts,received_at FROM messages WHERE last_error IS NOT NULL ORDER BY received_at DESC FETCH FIRST 50 ROWS ONLY;
