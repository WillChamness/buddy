from decimal import Decimal
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from buddy.dtos import BudgetExpenseDto
from buddy.src import dependencies
from buddy.src.data import BudgetExpenseRepository
from buddy.src.models import BudgetExpense, User

router = APIRouter(prefix="/budgeting", tags=["budgeting"])


@router.post("/income")
def add_income_source():
    raise NotImplementedError()


@router.get("/income/me")
def get_income(
    self,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
):
    raise NotImplementedError()


@router.delete("/income/me/{income_type}")
def delete_income(
    self,
    income_type: str,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
):
    raise NotImplementedError()


@router.get("/income/user/{user_id}")
def get_user_income():
    raise NotImplementedError()


@router.get("/income/type/{income_type}")
def get_income_by_type():
    raise NotImplementedError()


@router.delete("/income/type/{income_type}")
def delete_user_income_by_type():
    raise NotImplementedError()


@router.post("/expenses/me", status_code=status.HTTP_201_CREATED)
def add_expense(
    monthly_expense: BudgetExpenseDto,
    db: Session = Depends(dependencies.session),
    user: User = Depends(dependencies.get_user_or_admin),
) -> BudgetExpenseDto:
    try:
        expense: BudgetExpense | None = BudgetExpenseRepository.create(
            monthly_expense.expense_type,
            Decimal(monthly_expense.amount),
            monthly_expense.description,
            user,
            db,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your expense type is an empty string or contains bad whitespace",
        )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have '{monthly_expense.expense_type}' as an expense",
        )

    return BudgetExpenseDto(
        expense_type=expense.expense_type,
        amount=expense.amount,
        description=expense.description,
    )


@router.get("/expenses/me", status_code=status.HTTP_200_OK)
def get_expenses(
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[BudgetExpenseDto]:
    expenses: Iterable[BudgetExpense] = BudgetExpenseRepository.get_expenses(user, db)

    for expense in expenses:
        yield BudgetExpenseDto(
            expense_type=expense.expense_type,
            amount=expense.amount,
            description=expense.description,
        )


@router.delete("/expenses/me/{expense_type}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_type: str,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> None:
    found_and_deleted: bool = BudgetExpenseRepository.delete_expense(
        user, expense_type, db
    )
    if not found_and_deleted:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Could not find expense '{expense_type}'"
        )


@router.get("/expenses/user/{user_id}", status_code=status.HTTP_200_OK)
def get_expenses_by_user_id(
    user_id: int,
    _: User = Depends(dependencies.get_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[BudgetExpenseDto]:
    expenses: Iterable[BudgetExpense] = BudgetExpenseRepository.get_expenses_by_user_id(
        user_id, db
    )

    for expense in expenses:
        yield BudgetExpenseDto(
            expense_type=expense.expense_type,
            amount=expense.amount,
            description=expense.description,
        )


@router.get("/expenses/type/{expense_type}", status_code=status.HTTP_200_OK)
def get_expenses_by_type(
    expense_type: str,
    _: User = Depends(dependencies.get_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[BudgetExpenseDto]:
    expenses: Iterable[BudgetExpense] = BudgetExpenseRepository.get_expenses_by_type(
        expense_type, db
    )

    for expense in expenses:
        yield BudgetExpenseDto(
            expense_type=expense.expense_type,
            amount=expense.amount,
            description=expense.description,
        )
