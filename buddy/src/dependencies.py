import logging
import os
from typing import Callable, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from buddy.src import db
from buddy.src.models import User, UserRoles
from buddy.src.security import IdentitySecurity

logging.getLogger("passlib").setLevel(logging.ERROR)

session: Callable[[], Generator[Session, None, None]]
if (
    os.getenv("APPLICATION_ENV") == "dev"
    or os.getenv("APPLICATION_ENV") == "development"
):
    session = db.start_inmemory_session()
elif (
    os.getenv("APPLICATION_ENV") == "prod"
    or os.getenv("APPLICATION_ENV") == "production"
):
    session = db.start_sqlite_session()
else:
    raise RuntimeError("Invalid APPLICATION_ENV setting")

oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oath2_scheme), db: Session = Depends(session)
) -> User:
    """
    Returns:
        User: the current user from the 'Authorization: Bearer ...' header
    """
    user: User | None = IdentitySecurity.get_user_from_jwt(token, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authentication": "Bearer"},
        )

    return user


def get_admin(user: User = Depends(get_current_user)) -> User:
    """
    Returns:
        User: the user if the JWT token comes from an admin
    """
    if user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access is forbidden",
        )
    return user


def get_user_or_admin(user: User = Depends(get_current_user)) -> User:
    """
    Returns:
        User: the user if the JWT token comes from an admin or user (i.e. not an inactive user)
    """
    if user.role != UserRoles.admin and user.role != UserRoles.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access is forbidden",
        )
    return user
