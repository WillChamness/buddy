from decimal import Decimal
from sqlmodel import SQLModel, Field


class MonthlyIncome(SQLModel, table=True): # type: ignore[call-arg]
    """
    Independent sources of expected income
    """
    id: int|None = Field(primary_key=True, default=None)
    income_type: str
    amount: Decimal = Field(default=0, decimal_places=2)
    user_id: int = Field(foreign_key="user.id")



