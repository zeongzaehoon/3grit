from datetime import datetime, timedelta
from enum import StrEnum
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Annotated
from dataclasses import dataclass

SECRET_KEY = "THIS_IS_SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


def create_access_token(
    payload: dict,
    role: Role,
    expires_delta: timedelta = timedelta(hours=6)
):
    expire = datetime.utcnow() + expires_delta
    payload.update(
        {
            "exp": expire,
            "role": role,
        }
    )
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

@dataclass
class CurrentUser:
    id: str
    role: Role

    def __str__(self):
        return f"{self.id}({self.role})"


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    role=payload.get("role")
    if not user_id or not role or role != Role.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return CurrentUser(user_id, Role(role))


def get_admin_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)

    role=payload.get("role")
    # role = Role.ADMIN
    if not role or role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # NOTE: 현재는 어드민 유저를 어떻게 관리할지 정해진 바 없음. 임의로 ID 부여.
    return CurrentUser("ADMIN_USER_ID", Role(role))
