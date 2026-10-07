SELECT v.vin,v.site_id,v.location_id FROM vehicles v JOIN locations l ON l.location_id=v.location_id WHERE v.site_id<>l.site_id OR l.active=FALSE;
