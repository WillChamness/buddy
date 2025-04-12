__all__ = ["AccountingIncomeDto", "NewAccountingIncome", "DeleteAccountingIncome"]
import datetime
from pydantic import BaseModel
from decimal import Decimal

class AccountingIncomeDto(BaseModel):
    income_type: str
    date: datetime.date|str
    amount: Decimal|float
    user_id: int

class NewAccountingIncome(BaseModel):
    income_type: str
    amount: Decimal|float
    date: datetime.date|str
    description: str|None

class DeleteAccountingIncome(BaseModel):
    income_type: str
    date: datetime.date|str
