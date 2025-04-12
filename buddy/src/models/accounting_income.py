import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class AccountingIncome(SQLModel, table=True): # type: ignore[call-arg]
    """
    Actual income for a month
    """
    income_type: str = Field(primary_key=True)
    date: datetime.date = Field(primary_key=True, default_factory=lambda : datetime.date.today())
    user_id: int = Field(primary_key=True, foreign_key="user.id")
    amount: Decimal = Field(default=0, decimal_places=2)
