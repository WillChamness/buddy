__all__ = ["MonthlyIncomeDto", "NewMonthlyIncome"]
from pydantic import BaseModel
from decimal import Decimal

class MonthlyIncomeDto(BaseModel):
    income_type: str
    amount: Decimal|float
    user_id: int

class NewMonthlyIncome(BaseModel):
    income_type: str
    amount: Decimal|float

