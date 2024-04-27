import os
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, UTC

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import User
from .const import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"])

def create_jwt_token(data: dict) -> str:
    _ed = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.now(UTC)
    exp = datetime.now(UTC) + _ed
    token_payload = data
    token_payload.update({"iat": iat, "exp": exp})

    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return token

def get_user_from_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_id = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    return user_id

def get_user(authorization: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> int:
    if authorization.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    token = authorization.credentials
    return get_user_from_token(token)
