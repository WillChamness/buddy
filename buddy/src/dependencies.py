import os as _os
from typing import Callable, Generator

from fastapi import Depends as _Depends, HTTPException as _HTTPException, status as _status
from fastapi.security import OAuth2PasswordBearer as _OAuth2PasswordBearer
from sqlmodel import Session

from buddy.src import db as _db
from buddy.src.models import User as _User, UserRoles as _UserRoles
from buddy.src.security import IdentitySecurity as _IdentitySecurity

session: Callable[[], Generator[Session, None, None]]
if _os.getenv("APPLICATION_ENV") == "dev":
    session = _db.start_inmemory_session()
elif _os.getenv("APPLICATION_ENV") == "prod":
    session = _db.start_sqlite_session()
else:
    raise RuntimeError("APPLICATION_ENV must be 'dev' or 'prod'")

oath2_scheme = _OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = _Depends(oath2_scheme), db: Session = _Depends(session)
) -> _User:
    """
    Returns:
        User: the current user from the 'Authorization: Bearer ...' header
    """
    user: _User | None = _IdentitySecurity.get_user_from_jwt(token, db)

    if user is None:
        raise _HTTPException(
            status_code=_status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authentication": "Bearer"},
        )

    return user


def get_admin(user: _User = _Depends(get_current_user)) -> _User:
    """
    Returns:
        User: the user if the JWT token comes from an admin
    """
    if user.role != _UserRoles.admin:
        raise _HTTPException(
            status_code=_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access is forbidden",
        )
    return user


def get_user_or_admin(user: _User = _Depends(get_current_user)) -> _User:
    """
    Returns:
        User: the user if the JWT token comes from an admin or user (i.e. not an inactive user)
    """
    if user.role != _UserRoles.admin and user.role != _UserRoles.user:
        raise _HTTPException(
            status_code=_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access is forbidden",
        )
    return user
