from pydantic import BaseModel

class Signup(BaseModel):
    username: str
    password: str

class Login(BaseModel):
    username: str
    password: str

class PasswordReset(BaseModel):
    password: str
