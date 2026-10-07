package roleos;
import java.time.Clock;
import java.util.*;
import java.util.concurrent.*;
public final class Application implements AutoCloseable {
 public final TerminalService service;public final Router router;private final ScheduledExecutorService scheduler;
 public Application(Map<String,String> env){Auth auth=new Auth(env);String url=env.getOrDefault("ROLEOS_DB_URL","jdbc:h2:file:./runtime/terminal;MODE=Oracle;DB_CLOSE_DELAY=-1");service=new TerminalService(new Database(url),Clock.systemUTC());router=new Router(service,auth,Integer.parseInt(env.getOrDefault("ROLEOS_RATE_LIMIT","120")));Worker worker=new Worker(service,env.getOrDefault("ROLEOS_ACK_URL","http://127.0.0.1:8091/ack"),env.get("ROLEOS_ACK_SECRET"));scheduler=Executors.newScheduledThreadPool(2,r->{Thread t=new Thread(r,"roleos-worker");t.setDaemon(true);return t;});scheduler.scheduleWithFixedDelay(()->{try{service.processOnce();}catch(RuntimeException e){Json.log("worker.unhandled_error","processor",Map.of("exception_class",e.getClass().getSimpleName()));}},200,200,TimeUnit.MILLISECONDS);scheduler.scheduleWithFixedDelay(()->{try{worker.dispatchOnce();}catch(RuntimeException e){Json.log("worker.unhandled_error","dispatcher",Map.of("exception_class",e.getClass().getSimpleName()));}},200,200,TimeUnit.MILLISECONDS);}

 public void close(){scheduler.shutdownNow();try{scheduler.awaitTermination(5,TimeUnit.SECONDS);}catch(InterruptedException e){Thread.currentThread().interrupt();}service.db.close();}
}
