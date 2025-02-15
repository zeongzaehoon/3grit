from utils.containers import Container
from utils.auth import get_current_user, CurrentUser, get_admin_user
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from user.application.user_service import UserService

router = APIRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


@router.post("", status_code=201)
@inject
async def create_user(
    user: CreateUserBody,
    # NOTE: 앞 장에서의 코드와 같이 UserService를 직접 생성하지 않고 주입받은 객체를 시용한다.
    user_service: UserService = Depends(Provide[Container.user_service])
    # user_service: Annotated[UserService, Depends(UserService)]
):
    created_user = await user_service.create_user(
        name=user.name,
        email=user.email,
        password=user.password,
    )

    return created_user


@router.post("/login")
@inject
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service])
):
    access_token = await user_service.login(
        email=form_data.username,
        password=form_data.password,
    )

    return {"access_token": access_token, "token_type": "bearer"}


class UpdateUserBody(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)

@router.put("", response_model=UserResponse)
@inject
async def update_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service])
):
    updated_user = await user_service.update_user(
        user_id=current_user.id,
        name=body.name,
        password=body.password,
    )

    return updated_user


class GetUsersResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]

@router.get("")
@inject
async def get_users(
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_current_user),  # TODO: 임시로 설정, 추후에 get_admin_user로 변경하기.
    user_service: UserService = Depends(Provide[Container.user_service])
) -> GetUsersResponse:
    total_count, users = await user_service.get_users(page, items_per_page)

    return {
        "total_count": total_count,
        "page": page,
        "users": users,
    }
