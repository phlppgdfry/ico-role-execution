SELECT partner_id,event_key,COUNT(*) AS duplicate_count FROM messages GROUP BY partner_id,event_key HAVING COUNT(*)>1;
