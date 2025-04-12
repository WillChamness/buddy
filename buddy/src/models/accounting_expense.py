import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field

class AccountingExpense(SQLModel, table=True): # type: ignore[call-arg]
    """
    Actual expense for a month
    """
    expense_type: str = Field(primary_key=True)
    amount: Decimal = Field(default=0, decimal_places=2)
    description: str|None
    date: datetime.date = Field(primary_key=True, default_factory=lambda : datetime.date.today())
    user_id: int = Field(foreign_key="user.id", primary_key=True)
