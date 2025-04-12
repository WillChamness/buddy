__all__ = ["AccessTokenDto"]
from typing import Literal
from pydantic import BaseModel

class AccessTokenDto(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


