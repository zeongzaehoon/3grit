"""
 3.2 회원 가입 유스테이스
    회원 가입 기능에 대한 요구 사항은 다음과 같다.
    1. 전달받은 이메일과 패스워드를 User 테이블에 저장한다.
    2. 이때 중복된 이메일이 존재한다면 에러를 발생시킨다.
    3. 패스워드는 사람이 읽지 못하게 암호화돼야 한다.
"""

from ulid import ULID
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException, Depends
from typing import Annotated
from user.domain.user import User
from user.domain.repository.user_repo import IUserRepository
from user.infra.repository.user_repo import UserRepository

class UserService:
    @inject
    def __init__(
            self,
            # user_repo: Annotated[IUserRepository, Depends(UserRepository)]
            # user_repo: IUserRepository = Depends(Provide[Container.user_repo])
            user_repo: IUserRepository,
    ):
        """_summary_
            1. 유저를 데이터베이스에 저장하는 저장소는 인프라 계층에 구현되어 있어야 한다.
                외부의 서비스를 다루는 모듈은 그 수준이 낮기 때문이다. 따라서 데이터를 저장하기 위해 IUserRepository를 사용한다. 의존성이 역전돼 있다.
        """
        self.user_repo = user_repo  # NOTE: 추후에 의존성 주입으로 변경할 예정.
        self.ulid = ULID()

    def create_user(self, name:str, email:str, password:str):
        now=datetime.now()
        user:User = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=password,
            created_at=now,
            updated_at=now,
        )
        self.user_repo.save(user)

        return user