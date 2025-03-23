import os
from typing import Callable, Generator
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool
from buddy.src.models import User, UserRoles
from buddy.src.security import PasswordSecurity

def start_sqlite_session() -> Callable[[], Generator[Session, None, None]]:
    DB_URI: str|None = os.getenv("DB_URI")
    if DB_URI is None:
        raise RuntimeError("DB_URI is not an environment variable")

    engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session 

    return get_session


def start_inmemory_session() -> Callable[[], Generator[Session, None, None]]:
    db_uri = "sqlite://"

    engine = create_engine(db_uri, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(User(username="admin", password=PasswordSecurity.hash("admin"), role=UserRoles.admin))
        session.add(User(username="user1", password=PasswordSecurity.hash("password"), role=UserRoles.user))
        session.add(User(username="user2", password=PasswordSecurity.hash("password"), role=UserRoles.user))
        session.add(User(username="user3", password=PasswordSecurity.hash("password"), role=UserRoles.user))
        session.add(User(username="inactiveuser", password=PasswordSecurity.hash("password"), role=UserRoles.inactive))
        session.commit()

    def get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    return get_session
