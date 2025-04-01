from decimal import Decimal
from typing import Iterable

from sqlmodel import Session, select

from buddy.src.models import BudgetExpense, User


class BudgetExpenseRepository:
    @staticmethod
    def _standardize_expense_type(expense_type: str) -> str:
        standardized: str = ""
        for word in expense_type.split(" "):
            if word == "":
                raise ValueError("Expense type contains too much whitespace")

            standardized += f"{word[0].upper()}{word[1:].lower()} "

        standardized = standardized[: len(standardized) - 1]  # to remove leading space
        return standardized

    @classmethod
    def create(
        cls,
        expense_type: str,
        amount: Decimal,
        description: str | None,
        user: User,
        db: Session,
    ) -> BudgetExpense | None:
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
            ValueError: if the expense type is empty, contains invalid whitespace, or contains too many spaces
        """
        assert user.id is not None

        if expense_type == "" or "\t" in expense_type:
            raise ValueError("Expense type is empty or contains invalid whitespace")
        standardized_expense_type: str = cls._standardize_expense_type(expense_type)

        existing_expense: BudgetExpense | None = db.exec(
            select(BudgetExpense)
            .where(BudgetExpense.user_id == user.id)
            .where(BudgetExpense.expense_type == standardized_expense_type)
        ).first()

        if existing_expense is not None:
            return None

        expense: BudgetExpense = BudgetExpense(
            expense_type=standardized_expense_type,
            amount=amount,
            user_id=user.id,
            description=description,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    @classmethod
    def get_expenses(cls, user: User, db: Session) -> Iterable[BudgetExpense]:
        expenses: Iterable[BudgetExpense] = db.exec(
            select(BudgetExpense).where(BudgetExpense.user_id == user.id)
        ).all()
        return expenses

    @classmethod
    def get_expenses_by_user_id(
        cls, user_id: int, db: Session
    ) -> Iterable[BudgetExpense]:
        expenses: Iterable[BudgetExpense] = db.exec(
            select(BudgetExpense).where(BudgetExpense.user_id == user_id)
        ).all()
        return expenses

    @classmethod
    def get_expenses_by_type(
        cls, expense_type: str, db: Session
    ) -> Iterable[BudgetExpense]:
        standardized_expense_type: str = cls._standardize_expense_type(expense_type)
        expenses: Iterable[BudgetExpense] = db.exec(
            select(BudgetExpense).where(
                BudgetExpense.expense_type == standardized_expense_type
            )
        ).all()
        return expenses

    @classmethod
    def delete_expense(cls, user: User, expense_type: str, db: Session) -> bool:
        """
        Deletes the user's expense

        Args:
            user (User): the user to delete the expense from
            expense_type (str): The type of the expense
            db (Session): The database session

        Returns:
            True if the user has the expense in the database and the expense was deleted; otherwise False
        """
        standardized_expense_type: str = cls._standardize_expense_type(expense_type)
        expense: BudgetExpense | None = db.exec(
            select(BudgetExpense)
            .where(BudgetExpense.user_id == user.id)
            .where(BudgetExpense.expense_type == standardized_expense_type)
        ).first()

        if expense is None:
            return False
        
        db.delete(expense)
        db.commit()
        return True
