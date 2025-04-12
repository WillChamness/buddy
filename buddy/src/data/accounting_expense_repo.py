import datetime
from decimal import Decimal
from typing import Iterable

from sqlmodel import Session, select

from buddy.src.models import AccountingExpense, User

def _standardize_expense_type(expense_type: str) -> str:
    standardized: str = ""
    for word in expense_type.split(" "):
        if word == "":
            raise ValueError("Expense type contains too much whitespace")

        standardized += f"{word[0].upper()}{word[1:].lower()} "

    standardized = standardized[: len(standardized) - 1]  # to remove leading space
    return standardized

def create(
    expense_type: str,
    amount: Decimal,
    date: datetime.date,
    description: str | None,
    user: User,
    db: Session,
) -> AccountingExpense | None:
    """
    Creates a new monthly expense

    Args:
        expense_type (str): The type of the expense
        amount (Decimal): The value of the expense
        description (str|None): A description of the expense
        user (User): The user that has this expense
        db (Session): The database session

    Returns:
        The newly created BudgetExpense object if the user doesn't
            have this expense in the database already; otherwise None

    Raises:
        ValueError: if the expense type is empty, contains invalid
        whitespace, or contains too many spaces
    """
    assert user.id is not None

    if expense_type == "" or "\t" in expense_type or "\n" in expense_type:
        raise ValueError("Expense Type is invalid")
    standardized_expense_type: str = _standardize_expense_type(expense_type)

    existing_expense: AccountingExpense | None = db.exec(
        select(AccountingExpense)
        .where(AccountingExpense.user_id == user.id)
        .where(AccountingExpense.date == date)
        .where(AccountingExpense.expense_type == standardized_expense_type)
    ).first()

    if existing_expense is not None:
        return None

    expense: AccountingExpense = AccountingExpense(
        expense_type=standardized_expense_type,
        amount=amount,
        user_id=user.id,
        description=description,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense

def get_all(user: User, db: Session) -> Iterable[AccountingExpense]:
    """
    Gets the user's expenses

    Args:
        user: The user that has the expenses
        db: The database session

    Returns:
        The user's monthly budget expenses
    """
    expenses: Iterable[AccountingExpense] = db.exec(
        select(AccountingExpense).where(AccountingExpense.user_id == user.id)
    ).all()
    return expenses

def get_by_user_id(
    user_id: int, db: Session
) -> Iterable[AccountingExpense]:
    """
    Gets all expenses by user ID

    Args:
        user_id: The user ID of the user that has the expenses
        db: The database session

    Returns:
        The user's monthly budget expenses
    """
    expenses: Iterable[AccountingExpense] = db.exec(
        select(AccountingExpense).where(AccountingExpense.user_id == user_id)
    ).all()
    return expenses

def get_by_type(
    expense_type: str, db: Session
) -> Iterable[AccountingExpense]:
    """
    Gets all expenses by expense type

    Args:
        expense_type: The type of the expenses
        db: The database session

    Returns:
        The expenses across all users
    """
    expenses: Iterable[AccountingExpense] = db.exec(
        select(AccountingExpense).where(
            AccountingExpense.expense_type.ilike(f"%{expense_type}%") # type: ignore[attr-defined]
        )
    ).all()
    return expenses

def delete(user: User, expense_type: str, date: datetime.date, db: Session) -> bool:
    """
    Deletes the user's expense

    Args:
        user (User): the user to delete the expense from
        expense_type (str): The type of the expense
        db (Session): The database session

    Returns:
        True if the user has the expense in the database
        and the expense was deleted; otherwise False
    """
    standardized_expense_type: str = _standardize_expense_type(expense_type)
    expense: AccountingExpense | None = db.exec(
        select(AccountingExpense)
        .where(AccountingExpense.user_id == user.id)
        .where(AccountingExpense.date == date)
        .where(AccountingExpense.expense_type == standardized_expense_type)
    ).first()

    if expense is None:
        return False

    db.delete(expense)
    db.commit()
    return True
