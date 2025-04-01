from decimal import Decimal
from sqlmodel import SQLModel, Field

class BudgetExpense(SQLModel, table=True): # type: ignore[call-arg]
    """
    Expected monthly expenses
    """
    id: int|None = Field(primary_key=True, default=None)
    expense_type: str = Field()
    amount: Decimal = Field(default=0, decimal_places=2)
    description: str|None
    user_id: int = Field(foreign_key="user.id")


