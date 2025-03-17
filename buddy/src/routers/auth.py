from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, APIRouter, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from buddy.src import dependencies
from buddy.src.models import User, UserRoles, RefreshToken, convert_expiry_to_utc
from buddy.src.security import PasswordSecurity, IdentitySecurity
from buddy.src.data import UserRepository
from buddy.dtos import Signup, PasswordReset, AccessTokenDto

router = APIRouter(tags=["auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: Signup, db: Session=Depends(dependencies.session)) -> None:
    ok: bool = PasswordSecurity.create_user(credentials.username, credentials.password, db)

    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{credentials.username}' already exists")

@router.post("/token", status_code=status.HTTP_201_CREATED)
def login(response: Response, form_data: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(dependencies.session)) -> AccessTokenDto:
    user: User|None = PasswordSecurity.authenticate(form_data.username, form_data.password, db)

    if user is None or user.role == UserRoles.inactive:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Incorrect username or password")

    refresh_token: RefreshToken = IdentitySecurity.create_refresh_token(user, db)
    corrected_expiry: datetime = convert_expiry_to_utc(refresh_token)
    max_age: float = (corrected_expiry - datetime.now(tz=timezone.utc)).total_seconds()

    response.set_cookie(key="refresh_token", value=refresh_token.token, max_age=int(max_age), httponly=True, samesite="lax")
    jwt: str = IdentitySecurity.create_access_token(user)

    return AccessTokenDto(access_token=jwt, token_type="bearer")

@router.post("/refresh", status_code=status.HTTP_201_CREATED)
def generate_access_token(response: Response, refresh_token: str|None = Cookie(), db: Session=Depends(dependencies.session)) -> AccessTokenDto:
    token: RefreshToken|None = IdentitySecurity.validate_refresh_token(refresh_token, db)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in.")

    new_refresh_token, jwt = IdentitySecurity.rotate_refresh_token(token, db)

    corrected_expiry: datetime = convert_expiry_to_utc(new_refresh_token)
    max_age: float = (corrected_expiry - datetime.now(tz=timezone.utc)).total_seconds()

    response.set_cookie(key="refresh_token", value=new_refresh_token.token, max_age=int(max_age), httponly=True, samesite="strict")
    return AccessTokenDto(access_token=jwt, token_type="bearer")

@router.patch("/passwd", status_code=status.HTTP_204_NO_CONTENT)
def change_password(new_password: PasswordReset, user: User=Depends(dependencies.get_user_or_admin), db: Session=Depends(dependencies.session)) -> None:
    UserRepository.change_password(user=user, new_password=new_password.password, db=db)


