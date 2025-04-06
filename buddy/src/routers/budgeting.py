from decimal import Decimal
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from buddy.dtos import BudgetExpenseDto, MonthlyIncomeDto, NewBudgetExpense, NewMonthlyIncome
from buddy.src import dependencies
from buddy.src.data import BudgetExpenseRepository, MonthlyIncomeRepository
from buddy.src.models import BudgetExpense, MonthlyIncome, User

router = APIRouter(prefix="/budgeting", tags=["budgeting"])


@router.post("/income/me", status_code=status.HTTP_201_CREATED)
def add_income_source(
    monthly_income: NewMonthlyIncome,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> MonthlyIncomeDto:
    try:
        income: MonthlyIncome | None = MonthlyIncomeRepository.create(
            user, monthly_income.income_type, Decimal(monthly_income.amount), db
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if income is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have income source '{monthly_income.income_type}'",
        )

    return MonthlyIncomeDto(income_type=income.income_type, amount=income.amount, user_id=income.user_id)


@router.get("/income/me", status_code=status.HTTP_200_OK)
def get_income(
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[MonthlyIncomeDto]:
    income_sources: Iterable[MonthlyIncome] = MonthlyIncomeRepository.get_all(user, db)
    for income in income_sources:
        yield MonthlyIncomeDto(income_type=income.income_type, amount=income.amount, user_id=income.user_id)


@router.delete("/income/me/{income_type}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    income_type: str,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> None:
    found_and_deleted: bool = MonthlyIncomeRepository.delete(user, income_type, db)
    if not found_and_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find income '{income_type}'",
        )


@router.get("/income/user/{user_id}", status_code=status.HTTP_200_OK)
def get_user_income(
    user_id: int,
    db: Session = Depends(dependencies.session),
    _: User = Depends(dependencies.get_admin),
) -> Iterable[MonthlyIncomeDto]:
    income_sources: Iterable[MonthlyIncome] = MonthlyIncomeRepository.get_by_user_id(
        user_id, db
    )
    for income in income_sources:
        yield MonthlyIncomeDto(income_type=income.income_type, amount=income.amount, user_id=income.user_id)


@router.get("/income/type/{income_type}", status_code=status.HTTP_200_OK)
def get_income_by_type(
    income_type: str,
    db: Session = Depends(dependencies.session),
    _: User = Depends(dependencies.get_admin),
):
    income_sources: Iterable[MonthlyIncome] = MonthlyIncomeRepository.get_by_type(
        income_type, db
    )
    for income in income_sources:
        yield MonthlyIncomeDto(income_type=income.income_type, amount=income.amount, user_id=income.user_id)


@router.post("/expenses/me", status_code=status.HTTP_201_CREATED)
def add_expense(
    monthly_expense: NewBudgetExpense,
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
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
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
        user_id=expense.user_id
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
            user_id=expense.user_id
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
            user_id=expense.user_id
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
            user_id=expense.user_id
        )
