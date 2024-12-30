from utils.containers import Container
from dependency_injector.wiring import inject, Provide
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from user.application.user_service import UserService

router = APIRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


@router.post("", status_code=201)
def create_user(
    user: CreateUserBody,
    # NOTE: 앞 장에서의 코드와 같이 UserService를 직접 생성하지 않고 주입받은 객체를 시용한다.
    user_service: UserService = Depends(Provide[Container.user_service])
    # user_service: Annotated[UserService, Depends(UserService)]
):
    created_user = user_service.create_user(
        name=user.name,
        email=user.email,
        password=user.password,
    )

    return created_user