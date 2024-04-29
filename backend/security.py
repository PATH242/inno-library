"""
This module contains the authentication and authorization related functions.
"""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from .const import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"])


def create_jwt_token(data: dict) -> str:
    """
    Create a JWT token with the given data.
    """

    _ed = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.now(UTC)
    exp = datetime.now(UTC) + _ed
    token_payload = data
    token_payload.update({"iat": iat, "exp": exp})

    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def get_user_from_token(token: str) -> int:
    """
    Get the user id from the given JWT token.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    return user_id


def get_user(
    authorization: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> int:
    """
    Get the user id from a given Authorization header.
    """

    if authorization.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme",
        )

    token = authorization.credentials
    return get_user_from_token(token)
