import sqlalchemy as sa
from sqlmodel import SQLModel, Field
from datetime import datetime, timedelta, timezone
from buddy.src.models.user import User

class _RefreshTokenSettings:
    expiry_delta = timedelta(days=1)

def _create_timestamp() -> datetime:
    current_time = datetime.now(tz=timezone.utc)
    return current_time + _RefreshTokenSettings.expiry_delta

class RefreshToken(SQLModel, table=True): # type: ignore[call-arg]
    token: str = Field(primary_key=True)
    expiry: datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False), default_factory=_create_timestamp)
    user_id: int = Field(foreign_key="user.id")


def convert_expiry_to_utc(refresh_token: RefreshToken) -> datetime:
    """
    Workaround for SQLmodel storing datetimes without timezone data

    Args:
        refresh_token (RefreshToken): the datetime in UTC without the timezone data

    Returns:
        datetime: the equivalent datetime with the timezone data
    """
    return refresh_token.expiry.replace(tzinfo=timezone.utc)
