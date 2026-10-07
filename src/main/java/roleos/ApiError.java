package roleos;

public final class ApiError extends RuntimeException {
  private static final long serialVersionUID = 1L;
  public final int status;
  public final String code;

  public ApiError(int status, String code, String message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}
