from sqlmodel import Session, select
from buddy.src.models import User
from buddy.src.security import PasswordSecurity

class UserRepository:
    @classmethod
    def get_by_id(cls, id: int, db: Session) -> User|None:
        return db.get(User, id)

    @classmethod
    def get_by_username(cls, username: str, db: Session) -> User|None:
        return db.exec(select(User).where(User.username == username)).first()

    @classmethod
    def change_password(cls, user: User, new_password: str, db: Session) -> bool:
        if new_password == "":
            return False

        user.password = PasswordSecurity.hash(new_password)
        db.add(user)
        db.commit()
        return True


    @classmethod
    def delete_user(cls, user: User, db: Session) -> None:
        db.delete(user)
        db.commit()
