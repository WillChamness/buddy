import os
import secrets
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlmodel import Session, select, func, col
from datetime import datetime, timedelta, timezone
from buddy.src.models import User, UserRoles, RefreshToken, convert_expiry_to_utc

class PasswordSecurity:
    _context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash(cls, password: str) -> str:
        """
        Salts and hashes the password

        Args:
            password: The cleartext password

        Returns:
            str: The salted and hashed password
        """
        return cls._context.hash(password)

    @classmethod 
    def create_user(cls, username: str, password: str, db: Session) -> bool:
        """
        Creates a new user in the database.

        Args:
            username (str): The username of the user
            password (str): The cleartext password of the user
            db: The database session

        Returns:
            bool: False if the username already exists in the database; otherwise True
        """
        existing_user: User|None = db.exec(select(User).where(User.username == username)).first()
        if existing_user is not None:
            return False

        hashed_password = cls.hash(password)

        new_user: User
        if db.exec(select(func.count(col(User.id)))).one() == 0:
            new_user = User(username=username, password=hashed_password, role=UserRoles.admin)
        else:
            new_user = User(username=username, password=hashed_password, role=UserRoles.user)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True

    @classmethod
    def authenticate(cls, username: str, password: str, db: Session) -> User|None:
        """
        Validates a username and password

        Args:
            username (str): The username of the user
            password (str): The cleartext password of the user
            db: The database session

        Returns:
            User|None: The user if the username and password was found; otherwise None
        """
        user: User|None = db.exec(select(User).where(User.username == username)).first()

        if user is None:
            return None
        elif not cls._context.verify(password, user.password):
            return None
        else:
            return user


class IdentitySecurity:
    class _JwtData(BaseModel):
        sub: str 
        id: int 
        exp: datetime

    _expiry_delta: timedelta = timedelta(minutes=10)
    _algorithm: str = "HS256"
    _jwt_secret_key: str|None = os.getenv("JWT_SECRET_KEY")

    @classmethod
    def create_refresh_token(cls, user: User, db: Session) -> RefreshToken:
        """
        Creates a refresh token and adds it to the database. 

        Args:
            user (User): The user to add the token to
            db (Session): The database session

        Returns:
            RefreshToken: The newly created refresh token
        """
        assert user.id is not None
        token = RefreshToken(token=secrets.token_hex(32), user_id=user.id)
        db.add(token)
        db.commit()
        db.refresh(token)

        return token


    @classmethod
    def rotate_refresh_token(cls, token: RefreshToken, db: Session) -> tuple[RefreshToken, str]:
        """
        Deletes the old refresh token and creates a new one. Also generates a new JWT string.

        Args:
            token (RefreshToken): The validated refresh token
            db (Session): The database session

        Returns:
            tuple[RefreshToken, str]: The refresh token and the JWT string
        """
        user: User|None = db.get(User, token.user_id)
        assert user is not None

        cls.remove_refresh_token(token, db)
        new_refresh_token: RefreshToken = cls.create_refresh_token(user, db)
        return (new_refresh_token, cls.create_access_token(user))
        

    @classmethod
    def remove_refresh_token(cls, token: RefreshToken, db: Session) -> None:
        db.delete(token)
        db.commit()


    @classmethod
    def validate_refresh_token(cls, token: str|None, db: Session) -> RefreshToken|None:
        """
        Finds the refresh token in the database

        Args:
            token (str|None): The refresh token in question
            db (Session): The database session

        Returns:
            RefreshToken|None: The refresh token, if it exists and isn't expired; otherwise None
        """
        if token is None:
            return None

        refresh_token: RefreshToken|None = db.get(RefreshToken, token)
        if refresh_token is None:
            return None

        expiry: datetime = convert_expiry_to_utc(refresh_token)
        now: datetime = datetime.now(tz=timezone.utc)
        if now > expiry:
            return None

        return refresh_token


    @classmethod
    def create_access_token(cls, user: User) -> str:
        """

        """
        if cls._jwt_secret_key is None:
            raise RuntimeError("Server does not have JWT secret key setting set")

        assert user.id is not None
        encode = dict(cls._JwtData(sub=user.username, id=user.id, exp=datetime.now(tz=timezone.utc)+cls._expiry_delta))
        return jwt.encode(encode, cls._jwt_secret_key, algorithm=cls._algorithm)


    @classmethod
    def get_user_from_jwt(cls, token: str, db: Session) -> User|None:
        """

        """
        if cls._jwt_secret_key is None:
            raise RuntimeError("Server does not have JWT secret key setting set")
        id: int
        username: str
        try:
            payload: dict = jwt.decode(token, cls._jwt_secret_key, algorithms=[cls._algorithm])
            id = int(payload["id"])
            username = payload["sub"]
        except JWTError:
            return None
        except KeyError:
            return None
        except ValueError:
            return None

        user: User|None = db.exec(select(User).where(User.username == username).where(User.id == id)).first()
        return user



