package roleos;
import com.sun.net.httpserver.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.concurrent.*;
public final class LocalServer {
 private LocalServer(){}
 public static void main(String[] args)throws Exception{var app=new Application(System.getenv());int port=Integer.parseInt(System.getenv().getOrDefault("ROLEOS_PORT","8090"));var server=HttpServer.create(new InetSocketAddress("127.0.0.1",port),30);ExecutorService requests=Executors.newFixedThreadPool(8);server.setExecutor(requests);
  server.createContext("/",exchange->{try{String path=exchange.getRequestURI().getPath();if(path.startsWith("/api/")||path.equals("/health")){byte[] input=exchange.getRequestBody().readNBytes(16385);var response=app.router.handle(exchange.getRequestMethod(),path,exchange.getRequestHeaders().getFirst("Authorization"),new String(input,StandardCharsets.UTF_8),exchange.getRequestHeaders().getFirst("X-Correlation-ID"));send(exchange,response.status(),response.contentType(),response.body().getBytes(StandardCharsets.UTF_8));}
   else{String file=switch(path){case "/","/index.html"->"index.html";case "/portal.js"->"portal.js";case "/style.css"->"style.css";default->null;};if(file==null)send(exchange,404,"text/plain",new byte[0]);else send(exchange,200,file.endsWith("js")?"text/javascript":file.endsWith("css")?"text/css":"text/html",Files.readAllBytes(Path.of("src/main/webapp",file)));}}
   catch(Exception e){if(exchange.getResponseCode()==-1)send(exchange,500,"text/plain","Local adapter failure".getBytes(StandardCharsets.UTF_8));}finally{exchange.close();}});
  Runtime.getRuntime().addShutdownHook(new Thread(()->{server.stop(0);requests.shutdownNow();app.close();}));server.start();Json.log("application.started","startup",java.util.Map.of("adapter","JDK HttpServer","port",port,"simulation",true));}
 private static void send(HttpExchange e,int code,String type,byte[] content)throws java.io.IOException{e.getResponseHeaders().set("Content-Type",type);e.getResponseHeaders().set("Cache-Control","no-store");e.getResponseHeaders().set("X-Content-Type-Options","nosniff");e.getResponseHeaders().set("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'");if(code==429)e.getResponseHeaders().set("Retry-After","60");e.sendResponseHeaders(code,content.length);e.getResponseBody().write(content);}
}
