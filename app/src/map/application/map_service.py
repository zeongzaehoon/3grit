from ulid import ULID
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException, Depends, status
from typing import Annotated
from user.domain.user import User
from user.domain.repository.user_repo import IUserRepository
from user.infra.repository.user_repo import UserRepository
from utils.auth import create_access_token, Role
from utils.crypto import Crypto


# class MapService:
#     @inject
#     def __init__(
#         self,
#         # map_repo: IMapRepository,
#     ):
#         # self.map_repo = map_repo

#     async def create_map(self, store_id: int, category_id: int, subcategory_id: int, name: str, mapx: float, mapy: float, kakao_map_id: str):
#         pass

#     async def get_map(self, kakao_map_id: str):
#         pass
