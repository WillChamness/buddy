import datetime
from decimal import Decimal
from typing import Iterable

from sqlmodel import Session, select

from buddy.src.models import AccountingIncome, User


def _standardize_income_type(income_type: str) -> str:
    standardized: str = ""
    for word in income_type.split(" "):
        if word == "":
            raise ValueError("Income Type contains too much whitespace")

        standardized += f"{word[0].upper()}{word[1:].lower()} "

    standardized = standardized[: len(standardized) - 1]  # to remove leading space
    return standardized

def create(
    income_type: str,
    amount: Decimal,
    date: datetime.date,
    user: User,
    db: Session,
) -> AccountingIncome | None:
    assert user.id is not None
    if income_type == "" or "\t" in income_type or "\n" in income_type:
        raise ValueError("Income Type is invalid")
    standardized_income_type: str = _standardize_income_type(income_type)

    existing_income_source: AccountingIncome | None = db.exec(
        select(AccountingIncome)
        .where(AccountingIncome.user_id == user.id)
        .where(AccountingIncome.date == date)
        .where(AccountingIncome.income_type == standardized_income_type)
    ).first()

    if existing_income_source is not None:
        return None

    income: AccountingIncome = AccountingIncome(
        income_type=standardized_income_type,
        amount=amount,
        date=date,
        user_id=user.id,
    )
    db.add(income)
    db.commit()
    db.refresh(income)
    return income

def get_all(user: User, db: Session) -> Iterable[AccountingIncome]:
    income: Iterable[AccountingIncome] = db.exec(
        select(AccountingIncome).where(AccountingIncome.user_id == user.id)
    ).all()
    return income

def get_by_user_id(user_id: int, db: Session) -> Iterable[AccountingIncome]:
    """ """
    income: Iterable[AccountingIncome] = db.exec(
        select(AccountingIncome).where(AccountingIncome.user_id == user_id)
    ).all()
    return income

def get_by_type(income_type: str, db: Session) -> Iterable[AccountingIncome]:
    """ """
    income: Iterable[AccountingIncome] = db.exec(
        select(AccountingIncome).filter(
            AccountingIncome.income_type.ilike(f"%{income_type}%")  # type: ignore[attr-defined]
        )
    ).all()
    return income

def delete(
    user: User, income_type: str, date: datetime.date, db: Session
) -> bool:
    """
    Deletes the user's income

    Args:
        user (User): the user to delete the expense from
        expense_type (str): The type of the expense
        db (Session): The database session

    Returns:
        True if the user has the income source in the database
        and it was deleted; otherwise False
    """
    standardized_income_type: str = _standardize_income_type(income_type)
    income: AccountingIncome | None = db.exec(
        select(AccountingIncome)
        .where(AccountingIncome.user_id == user.id)
        .where(AccountingIncome.date == date)
        .where(AccountingIncome.income_type == standardized_income_type)
    ).first()

    if income is None:
        return False

    db.delete(income)
    db.commit()
    return True

