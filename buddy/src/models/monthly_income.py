from decimal import Decimal
from sqlmodel import SQLModel, Field


class MonthlyIncome(SQLModel, table=True): # type: ignore[call-arg]
    """
    Independent sources of expected income
    """
    income_type: str = Field(primary_key=True)
    user_id: int = Field(primary_key=True, foreign_key="user.id")
    amount: Decimal = Field(default=0, decimal_places=2)



