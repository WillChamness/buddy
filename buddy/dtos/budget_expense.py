__all__ = ["BudgetExpenseDto", "NewBudgetExpense"]
from pydantic import BaseModel
from decimal import Decimal

class BudgetExpenseDto(BaseModel):
    expense_type: str
    amount: Decimal|float
    description: str|None
    user_id: int

class NewBudgetExpense(BaseModel):
    expense_type: str
    amount: Decimal|float
    description: str|None
