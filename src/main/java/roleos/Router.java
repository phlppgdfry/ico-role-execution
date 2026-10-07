package roleos;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.regex.*;
public final class Router {
 public record Response(int status,String contentType,String body){}
 private final TerminalService service;private final Auth auth;private final int rateLimit;private final Map<String,long[]> rates=new HashMap<>();
 private final AtomicLong requests=new AtomicLong(),errors=new AtomicLong(),elapsed=new AtomicLong(),completed=new AtomicLong();
 public Router(TerminalService service,Auth auth,int rateLimit){this.service=service;this.auth=auth;this.rateLimit=rateLimit;}
 private synchronized void rate(Auth.Actor actor){long minute=service.clock.millis()/60_000;long[] bucket=rates.computeIfAbsent(actor.name(),k->new long[]{minute,0});if(bucket[0]!=minute){bucket[0]=minute;bucket[1]=0;}if(++bucket[1]>rateLimit)throw new ApiError(429,"RATE_LIMITED","Retry after the next minute boundary");}
 public Response handle(String method,String path,String authorization,String body,String suppliedCorrelation){String correlation=suppliedCorrelation!=null&&suppliedCorrelation.matches("[A-Za-z0-9_-]{1,64}")?suppliedCorrelation:TerminalService.uuid();long start=System.nanoTime();requests.incrementAndGet();Response response;
  try{
   if(method.equals("GET")&&path.equals("/health")){service.db.query("SELECT 1 AS ok");boolean ready=!service.db.flag("force_api_failure");response=json(ready?200:503,Map.of("status",ready?"READY":"DEGRADED","version","1.4.0","simulation",true));}
   else{Auth.Actor actor=auth.authenticate(authorization);rate(actor);if(body.getBytes(java.nio.charset.StandardCharsets.UTF_8).length>16384)throw new ApiError(413,"PAYLOAD_TOO_LARGE","Maximum request body is 16 KiB");
    if(service.db.flag("force_api_failure")&&!path.equals("/api/admin/controls"))throw new ApiError(503,"SANDBOX_DEPENDENCY_FAILURE","Fault active; lab admin may recover controls");
    response=route(method,path,body,actor,correlation);
   }
  }catch(ApiError e){errors.incrementAndGet();response=json(e.status,Map.of("error",e.code,"message",e.getMessage(),"correlation_id",correlation));}
  catch(RuntimeException e){errors.incrementAndGet();Json.log("request.internal_error",correlation,Map.of("exception_class",e.getClass().getSimpleName()));response=json(500,Map.of("error","INTERNAL_ERROR","message","Use correlation id for investigation","correlation_id",correlation));}
  finally{elapsed.addAndGet(System.nanoTime()-start);completed.incrementAndGet();}
  Json.log("request.completed",correlation,Map.of("method",method,"path",path,"status",response.status));return response;
 }
 private Response route(String method,String path,String body,Auth.Actor actor,String correlation){
  if(method.equals("POST")&&path.equals("/api/messages")){var receipt=service.accept(Json.read(body),actor,correlation);return json(receipt.duplicate()?200:202,receipt);}
  if(method.equals("GET")&&(path.equals("/api/messages")||path.equals("/api/vehicles"))){actor.require("PARTNER","READER","OPERATOR","ADMIN");return json(200,service.scoped(path.endsWith("messages")?"messages":"vehicles",actor));}
  if(method.equals("GET")&&path.startsWith("/api/messages/")){String id=path.substring("/api/messages/".length());var msg=Database.first(service.db.query("SELECT id,partner_id,site_id,event_key,status,attempts,last_error,received_at,processed_at FROM messages WHERE id=?",id));if(msg==null||!actor.canSee(msg))throw new ApiError(404,"NOT_FOUND","Message absent in scope");return json(200,msg);}
  if(method.equals("GET")&&path.equals("/api/reports/occupancy"))return json(200,service.report(actor));
  if(method.equals("GET")&&path.equals("/api/reports/occupancy.csv")){StringBuilder csv=new StringBuilder("site_id,partner_id,state,vehicle_count,held_count\n");for(var row:service.report(actor))csv.append(row.get("site_id")).append(',').append(row.get("partner_id")).append(',').append(row.get("state")).append(',').append(row.get("vehicle_count")).append(',').append(row.get("held_count")).append('\n');return new Response(200,"text/csv; charset=utf-8",csv.toString());}
  if(method.equals("GET")&&path.equals("/api/metrics")){actor.require("READER","OPERATOR","ADMIN");var metrics=service.metrics();metrics.put("http_requests",requests.get());metrics.put("http_errors",errors.get());metrics.put("mean_request_ms",completed.get()==0?0:elapsed.get()/1_000_000.0/completed.get());return json(200,metrics);}
  if(method.equals("GET")&&path.startsWith("/api/admin/diagnostics/")){actor.require("ADMIN");return json(200,service.db.diagnostic(path.substring("/api/admin/diagnostics/".length())));}
  if(method.equals("GET")&&path.equals("/api/audit")){actor.require("ADMIN");return json(200,service.db.query("SELECT * FROM audit_log ORDER BY created_at DESC,id FETCH FIRST 200 ROWS ONLY"));}
  if(path.equals("/api/admin/controls")){actor.require("ADMIN");if(method.equals("GET"))return json(200,service.db.query("SELECT * FROM controls ORDER BY control_name"));if(method.equals("PATCH")){service.controls(Json.read(body),actor,correlation);return json(200,Map.of("updated",true));}}
  Matcher redrive=Pattern.compile("/api/messages/([a-f0-9-]{36})/redrive").matcher(path);if(method.equals("POST")&&redrive.matches()){var n=Json.read(body);Json.allowed(n,Set.of("reason"));service.redrive(redrive.group(1),actor,Json.required(n,"reason",240),correlation);return json(200,Map.of("status","RECEIVED"));}
  Matcher vehicle=Pattern.compile("/api/vehicles/([A-Z0-9]{17})/(location|hold)").matcher(path);if(method.equals("PUT")&&vehicle.matches())return json(200,service.correct(vehicle.group(1),Json.read(body),actor,correlation,vehicle.group(2).equals("hold")));
  throw new ApiError(404,"NOT_FOUND","Unknown route or method");
 }
 private static Response json(int status,Object body){return new Response(status,"application/json; charset=utf-8",Json.write(body));}
}
