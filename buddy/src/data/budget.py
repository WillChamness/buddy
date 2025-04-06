from decimal import Decimal
from typing import Iterable

from sqlmodel import Session, select

from buddy.src.models import BudgetExpense, MonthlyIncome, User


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
            ValueError: if the expense type is empty, contains invalid
            whitespace, or contains too many spaces
        """
        assert user.id is not None

        if expense_type == "" or "\t" in expense_type or "\n" in expense_type:
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
        """
        Gets the user's expenses

        Args:
            user: The user that has the expenses
            db: The database session

        Returns:
            The user's monthly budget expenses
        """
        expenses: Iterable[BudgetExpense] = db.exec(
            select(BudgetExpense).where(BudgetExpense.user_id == user.id)
        ).all()
        return expenses

    @classmethod
    def get_expenses_by_user_id(
        cls, user_id: int, db: Session
    ) -> Iterable[BudgetExpense]:
        """
        Gets all expenses by user ID

        Args:
            user_id: The user ID of the user that has the expenses
            db: The database session

        Returns:
            The user's monthly budget expenses
        """
        expenses: Iterable[BudgetExpense] = db.exec(
            select(BudgetExpense).where(BudgetExpense.user_id == user_id)
        ).all()
        return expenses

    @classmethod
    def get_expenses_by_type(
        cls, expense_type: str, db: Session
    ) -> Iterable[BudgetExpense]:
        """
        Gets all expenses by expense type

        Args:
            expense_type: The type of the expenses
            db: The database session

        Returns:
            The expenses across all users
        """
        expenses: Iterable[BudgetExpense] = db.exec(
            select(BudgetExpense).where(
                BudgetExpense.expense_type.ilike(f"%{expense_type}%") # type: ignore[attr-defined]
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
            True if the user has the expense in the database
            and the expense was deleted; otherwise False
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


class MonthlyIncomeRepository:
    @staticmethod
    def _standardize_income_type(income_type: str) -> str:
        standardized: str = ""
        for word in income_type.split(" "):
            if word == "":
                raise ValueError("Expense type contains too much whitespace")

            standardized += f"{word[0].upper()}{word[1:].lower()} "

        standardized = standardized[: len(standardized) - 1]  # to remove leading space
        return standardized

    @classmethod
    def create(
        cls, user: User, income_type: str, amount: Decimal, db: Session
    ) -> MonthlyIncome | None:
        assert user.id is not None

        if income_type == "" or "\t" in income_type or "\n" in income_type:
            raise ValueError("Expense type is empty or contains invalid whitespace")
        standardized_income_type: str = cls._standardize_income_type(income_type)

        existing_income_source: MonthlyIncome | None = db.exec(
            select(MonthlyIncome)
            .where(MonthlyIncome.user_id == user.id)
            .where(MonthlyIncome.income_type == standardized_income_type)
        ).first()

        if existing_income_source is not None:
            return None

        income: MonthlyIncome = MonthlyIncome(
            income_type=standardized_income_type,
            amount=amount,
            user_id=user.id,
        )
        db.add(income)
        db.commit()
        db.refresh(income)
        return income

    @classmethod
    def get_all(cls, user: User, db: Session) -> Iterable[MonthlyIncome]:
        income: Iterable[MonthlyIncome] = db.exec(
            select(MonthlyIncome).where(MonthlyIncome.user_id == user.id)
        ).all()
        return income

    @classmethod
    def get_by_user_id(cls, user_id: int, db: Session) -> Iterable[MonthlyIncome]:
        """ """
        income: Iterable[MonthlyIncome] = db.exec(
            select(MonthlyIncome).where(MonthlyIncome.user_id == user_id)
        ).all()
        return income

    @classmethod
    def get_by_type(cls, income_type: str, db: Session) -> Iterable[MonthlyIncome]:
        """ """
        income: Iterable[MonthlyIncome] = db.exec(
            select(MonthlyIncome).filter(
                MonthlyIncome.income_type.ilike(f"%{income_type}%") # type: ignore[attr-defined]
            )
        ).all()
        return income

    @classmethod
    def delete(cls, user: User, income_type: str, db: Session) -> bool:
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
        standardized_income_type: str = cls._standardize_income_type(income_type)
        income: MonthlyIncome | None = db.exec(
            select(MonthlyIncome)
            .where(MonthlyIncome.user_id == user.id)
            .where(MonthlyIncome.income_type == standardized_income_type)
        ).first()

        if income is None:
            return False

        db.delete(income)
        db.commit()
        return True
