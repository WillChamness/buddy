from buddy.src import dependencies
from fastapi import APIRouter, HTTPException, status, Depends
from buddy.src.models import User
from buddy.dtos import UserDto
from buddy.src.data import UserRepository
from sqlmodel import Session

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/id/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: Session=Depends(dependencies.session), _: User=Depends(dependencies.get_admin)) -> UserDto:
    searched_user: User|None = UserRepository.get_by_id(user_id, db)
    if searched_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID '{user_id}' not found")

    assert searched_user.id is not None
    return UserDto(id=searched_user.id, username=searched_user.username, role=searched_user.role.value)

@router.get("/username/{username}", status_code=status.HTTP_200_OK)
def get_user_by_username(username: str, db: Session=Depends(dependencies.session), _: User=Depends(dependencies.get_admin)) -> UserDto:
    searched_user: User|None = UserRepository.get_by_username(username, db)
    if searched_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username '{username}' not found")

    assert searched_user.id is not None
    return UserDto(id=searched_user.id, username=searched_user.username, role=searched_user.role.value)

@router.get("/me", status_code=status.HTTP_200_OK)
def get_user_profile(user: User=Depends(dependencies.get_user_or_admin)) -> UserDto:
    assert user.id is not None
    return UserDto(id=user.id, username=user.username, role=user.role.value)

@router.delete("/delete/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: Session=Depends(dependencies.session), user: User=Depends(dependencies.get_user_or_admin)) -> None:
    UserRepository.delete_user(user, db)

@router.delete("/delete/id/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(user_id: int, db: Session=Depends(dependencies.session), _: User=Depends(dependencies.get_admin)) -> None:
    user_to_delete: User|None = UserRepository.get_by_id(user_id, db)
    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID '{user_id}' not found")
    UserRepository.delete_user(user_to_delete, db)
