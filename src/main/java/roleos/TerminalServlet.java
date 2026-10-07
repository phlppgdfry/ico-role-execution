package roleos;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
/** Real WAR adapter. Container lifecycle owns the scheduler. */
public final class TerminalServlet extends HttpServlet {
 private static final long serialVersionUID=1L;private transient Application app;
 @Override public void init()throws ServletException{try{app=new Application(System.getenv());}catch(RuntimeException e){throw new ServletException("RoleOS configuration failed",e);}}
 @Override protected void service(HttpServletRequest request,HttpServletResponse response)throws IOException{String path=request.getServletPath()+((request.getPathInfo()==null)?"":request.getPathInfo());byte[] body=request.getInputStream().readNBytes(16385);var result=app.router.handle(request.getMethod(),path,request.getHeader("Authorization"),new String(body,StandardCharsets.UTF_8),request.getHeader("X-Correlation-ID"));response.setStatus(result.status());response.setContentType(result.contentType());response.setHeader("Cache-Control","no-store");response.setHeader("X-Content-Type-Options","nosniff");if(result.status()==429)response.setHeader("Retry-After","60");response.getWriter().write(result.body());}
 @Override public void destroy(){if(app!=null)app.close();}
}
