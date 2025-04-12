from datetime import date, datetime
from decimal import Decimal
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from buddy.dtos import (AccountingExpenseDto, AccountingIncomeDto,
                        DeleteAccountingExpense, DeleteAccountingIncome,
                        NewAccountingExpense, NewAccountingIncome)
from buddy.src import dependencies
from buddy.src.data import accounting_expense_repo, accounting_income_repo
from buddy.src.models import AccountingExpense, AccountingIncome, User

router = APIRouter(prefix="/accounting", tags=["accounting"])


def _convert_str_to_date(date_str: date | str) -> date:
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


@router.post("/income/me", status_code=status.HTTP_201_CREATED)
def add_income_source(
    accounting_income: NewAccountingIncome,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> AccountingIncomeDto:
    accounting_income.date = _convert_str_to_date(accounting_income.date)
    try:
        income: AccountingIncome | None = accounting_income_repo.create(
            income_type=accounting_income.income_type,
            amount=Decimal(accounting_income.amount),
            date=accounting_income.date,
            user=user,
            db=db,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if income is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have income source '{accounting_income.income_type}'",
        )
    return AccountingIncomeDto(
        income_type=income.income_type,
        amount=income.amount,
        user_id=income.user_id,
        date=income.date,
    )


@router.get("/income/me", status_code=status.HTTP_200_OK)
def get_income(
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[AccountingIncomeDto]:
    income_sources: Iterable[AccountingIncome] = accounting_income_repo.get_all(
        user, db
    )
    for income in income_sources:
        yield AccountingIncomeDto(
            income_type=income.income_type,
            amount=income.amount,
            user_id=income.user_id,
            date=income.date,
        )


@router.delete("/income/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    delete_income_request: DeleteAccountingIncome,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> None:
    delete_income_request.date = _convert_str_to_date(delete_income_request.date)
    found_and_deleted: bool = accounting_income_repo.delete(
        user, delete_income_request.income_type, delete_income_request.date, db
    )
    if not found_and_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find income '{delete_income_request.income_type}'",
        )


@router.get("/income/user/{user_id}", status_code=status.HTTP_200_OK)
def get_user_income(
    user_id: int,
    db: Session = Depends(dependencies.session),
    _: User = Depends(dependencies.get_admin),
) -> Iterable[AccountingIncomeDto]:
    income_sources: Iterable[AccountingIncome] = accounting_income_repo.get_by_user_id(
        user_id, db
    )
    for income in income_sources:
        yield AccountingIncomeDto(
            income_type=income.income_type,
            amount=income.amount,
            user_id=income.user_id,
            date=income.date,
        )


@router.get("/income/type/{income_type}", status_code=status.HTTP_200_OK)
def get_income_by_type(
    income_type: str,
    db: Session = Depends(dependencies.session),
    _: User = Depends(dependencies.get_admin),
):
    income_sources: Iterable[AccountingIncome] = accounting_income_repo.get_by_type(
        income_type, db
    )
    for income in income_sources:
        yield AccountingIncomeDto(
            income_type=income.income_type,
            amount=income.amount,
            user_id=income.user_id,
            date=income.date,
        )


@router.post("/expenses/me", status_code=status.HTTP_201_CREATED)
def add_expense(
    monthly_expense: NewAccountingExpense,
    db: Session = Depends(dependencies.session),
    user: User = Depends(dependencies.get_user_or_admin),
) -> AccountingExpenseDto:
    try:
        expense: AccountingExpense | None = accounting_expense_repo.create(
            monthly_expense.expense_type,
            Decimal(monthly_expense.amount),
            _convert_str_to_date(monthly_expense.date),
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

    return AccountingExpenseDto(
        expense_type=expense.expense_type,
        amount=expense.amount,
        description=expense.description,
        user_id=expense.user_id,
        date=expense.date,
    )


@router.get("/expenses/me", status_code=status.HTTP_200_OK)
def get_expenses(
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[AccountingExpenseDto]:
    expenses: Iterable[AccountingExpense] = accounting_expense_repo.get_all(user, db)

    for expense in expenses:
        yield AccountingExpenseDto(
            expense_type=expense.expense_type,
            amount=expense.amount,
            description=expense.description,
            user_id=expense.user_id,
            date=expense.date,
        )


@router.delete("/expenses/me/", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    delete_accounting_income: DeleteAccountingExpense,
    user: User = Depends(dependencies.get_user_or_admin),
    db: Session = Depends(dependencies.session),
) -> None:
    found_and_deleted: bool = accounting_expense_repo.delete(
        user,
        delete_accounting_income.expense_type,
        _convert_str_to_date(delete_accounting_income.date),
        db,
    )
    if not found_and_deleted:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Could not find expense '{DeleteAccountingExpense.expense_type}'",
        )


@router.get("/expenses/user/{user_id}", status_code=status.HTTP_200_OK)
def get_expenses_by_user_id(
    user_id: int,
    _: User = Depends(dependencies.get_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[AccountingExpenseDto]:
    expenses: Iterable[AccountingExpense] = accounting_expense_repo.get_by_user_id(
        user_id, db
    )

    for expense in expenses:
        yield AccountingExpenseDto(
            expense_type=expense.expense_type,
            amount=expense.amount,
            description=expense.description,
            user_id=expense.user_id,
            date=expense.date,
        )


@router.get("/expenses/type/{expense_type}", status_code=status.HTTP_200_OK)
def get_expenses_by_type(
    expense_type: str,
    _: User = Depends(dependencies.get_admin),
    db: Session = Depends(dependencies.session),
) -> Iterable[AccountingExpenseDto]:
    expenses: Iterable[AccountingExpense] = accounting_expense_repo.get_by_type(
        expense_type, db
    )

    for expense in expenses:
        yield AccountingExpenseDto(
            expense_type=expense.expense_type,
            amount=expense.amount,
            description=expense.description,
            user_id=expense.user_id,
            date=expense.date,
        )
