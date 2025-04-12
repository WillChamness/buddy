from decimal import Decimal
from sqlmodel import SQLModel, Field

class BudgetExpense(SQLModel, table=True): # type: ignore[call-arg]
    """
    Expected monthly expenses
    """
    expense_type: str = Field(primary_key=True)
    user_id: int = Field(primary_key=True, foreign_key="user.id")
    amount: Decimal = Field(default=0, decimal_places=2)
    description: str|None


