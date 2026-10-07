SELECT site_id,partner_id,state,COUNT(*) AS vehicle_count,SUM(CASE WHEN hold_flag THEN 1 ELSE 0 END) AS held_count FROM vehicles GROUP BY site_id,partner_id,state ORDER BY site_id,partner_id,state;
