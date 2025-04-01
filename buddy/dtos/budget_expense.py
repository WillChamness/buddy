from typing_extensions import Annotated
from pydantic import BaseModel
from pydantic.functional_serializers import PlainSerializer
from decimal import Decimal

class BudgetExpenseDto(BaseModel):
    expense_type: str
    amount: float|Annotated[Decimal, PlainSerializer(lambda amt : str(amt), return_type=str, when_used="json")] 
    description: str|None
