from enum import Enum

from sqlmodel import Field, SQLModel


class UserRoles(Enum):
    user = "user"
    admin = "admin"
    inactive = "inactive"


class User(SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = Field(primary_key=True, default=None)
    username: str
    password: str
    role: UserRoles
