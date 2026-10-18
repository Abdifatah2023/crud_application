from fastapi import Depends, Header

import repository


class Unauthorized(Exception):
    """Raised by the auth guard; main.py turns it into a 401 {"error": ...} response."""

    def __init__(self, message: str):
        self.message = message


def extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    token = extract_bearer_token(authorization)
    if token is None:
        raise Unauthorized("Access token required")
    return token


def get_current_user(token: str = Depends(get_bearer_token)):
    user = repository.get_user_from_token(token)
    if user is None:
        raise Unauthorized("Invalid or expired token")
    return user
