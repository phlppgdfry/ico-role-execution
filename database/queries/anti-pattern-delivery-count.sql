-- Demonstration only: wrong grain. NEVER use as operational vehicle report.
SELECT v.site_id,COUNT(*) AS incorrect_vehicle_count FROM vehicles v JOIN messages m ON m.vin=v.vin JOIN deliveries d ON d.message_id=m.id GROUP BY v.site_id;
