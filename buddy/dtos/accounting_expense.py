__all__ = ["AccountingExpenseDto", "NewAccountingExpense", "DeleteAccountingExpense"]
import datetime
from pydantic import BaseModel
from decimal import Decimal

class AccountingExpenseDto(BaseModel):
    user_id: int
    expense_type: str
    date: datetime.date|str
    amount: Decimal|float
    description: str|None

class NewAccountingExpense(BaseModel):
    expense_type: str
    amount: Decimal|float
    date: datetime.date|str
    description: str|None

class DeleteAccountingExpense(BaseModel):
    expense_type: str
    date: datetime.date|str
