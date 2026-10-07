package roleos;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
public final class Auth {
 public record Actor(String name,String role,String partner,Set<String> sites){public void require(String...roles){if(Arrays.stream(roles).noneMatch(role::equals))throw new ApiError(403,"FORBIDDEN","Role not allowed");}public boolean canSee(Map<String,Object> row){return sites.contains(row.get("site_id"))&&(partner==null||partner.equals(row.get("partner_id")));}}
 private record Credential(byte[] token,Actor actor){}
 private final List<Credential> credentials=new ArrayList<>();
 public Auth(Map<String,String> env){
  add(env,"ROLEOS_ALPHA_TOKEN",new Actor("alpha-service","PARTNER","ALPHA",Set.of("ZEE","KAL")));
  add(env,"ROLEOS_BETA_TOKEN",new Actor("beta-service","PARTNER","BETA",Set.of("KAL")));
  add(env,"ROLEOS_READER_TOKEN",new Actor("report-reader","READER",null,Set.of("ZEE","KAL")));
  add(env,"ROLEOS_OPERATOR_TOKEN",new Actor("operations-user","OPERATOR",null,Set.of("ZEE","KAL")));
  add(env,"ROLEOS_ADMIN_TOKEN",new Actor("lab-approver","ADMIN",null,Set.of("ZEE","KAL")));
 }
 private void add(Map<String,String> env,String name,Actor actor){String token=env.get(name);if(token==null||token.length()<24)throw new IllegalArgumentException("Set a random 24+ character "+name);if(credentials.stream().anyMatch(c->MessageDigest.isEqual(c.token,token.getBytes(StandardCharsets.UTF_8))))throw new IllegalArgumentException("Tokens must be distinct");credentials.add(new Credential(token.getBytes(StandardCharsets.UTF_8),actor));}
 public Actor authenticate(String header){if(header==null||!header.startsWith("Bearer "))throw new ApiError(401,"UNAUTHENTICATED","Bearer required");byte[] supplied=header.substring(7).getBytes(StandardCharsets.UTF_8);for(Credential c:credentials)if(MessageDigest.isEqual(c.token,supplied))return c.actor;throw new ApiError(401,"UNAUTHENTICATED","Token rejected");}
}
