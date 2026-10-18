from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import repository


# Registers the "Bearer" security scheme in OpenAPI, which gives Swagger UI its Authorize padlock.
# auto_error=False so a missing token reaches our own 401 {"error": ...} instead of FastAPI's default.
bearer_scheme = HTTPBearer(
    auto_error=False,
    bearerFormat="JWT",
    description="Paste the access_token returned by POST /auth/login.",
)


class Unauthorized(Exception):
    """Raised by the auth guard; main.py turns it into a 401 {"error": ...} response."""

    def __init__(self, message: str):
        self.message = message


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    # HTTPBearer returns None when the header is missing, isn't "Bearer ...", or has no token.
    token = credentials.credentials.strip() if credentials else ""
    if not token:
        raise Unauthorized("Access token required")
    return token


def get_current_user(token: str = Depends(get_bearer_token)):
    user = repository.get_user_from_token(token)
    if user is None:
        raise Unauthorized("Invalid or expired token")
    return user
