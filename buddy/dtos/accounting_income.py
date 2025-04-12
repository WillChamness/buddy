__all__ = ["AccountingIncomeDto", "NewAccountingIncome", "DeleteAccountingIncome"]
import datetime
from pydantic import BaseModel
from decimal import Decimal

class AccountingIncomeDto(BaseModel):
    user_id: int
    income_type: str
    date: datetime.date|str
    amount: Decimal|float

class NewAccountingIncome(BaseModel):
    income_type: str
    amount: Decimal|float
    date: datetime.date|str

class DeleteAccountingIncome(BaseModel):
    income_type: str
    date: datetime.date|str
