__all__ = ["AccountingExpenseDto", "NewAccountingExpense", "DeleteAccountingExpense"]
import datetime
from pydantic import BaseModel
from decimal import Decimal

class AccountingExpenseDto(BaseModel):
    expense_type: str
    date: datetime.date|str
    amount: Decimal|float
    description: str|None
    user_id: int

class NewAccountingExpense(BaseModel):
    expense_type: str
    amount: Decimal|float
    description: str|None
    date: datetime.date|str

class DeleteAccountingExpense(BaseModel):
    expense_type: str
    date: datetime.date|str
