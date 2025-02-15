from utils.database import SessionLocal
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.user import User
from fastapi import HTTPException
from sqlalchemy import select, func
from utils.helpers import row_to_dict


class UserRepository(IUserRepository):
    async def save(self, user:UserVO):
        new_user = User(
            email=user.email,
            name=user.name,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        async with SessionLocal() as db:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            # Update the domain object with the generated id
            user.id = new_user.id

    async def get_users(
        self,
        page: int = 1,
        items_per_page: int = 10,
    ) -> tuple[int, list[UserVO]]:
        async with SessionLocal() as db:
            # Count 쿼리 실행
            count_query = select(func.count()).select_from(User)
            total_count = await db.scalar(count_query)

            # Pagination 쿼리 실행
            query = (
                select(User).limit(items_per_page).offset((page - 1) * items_per_page)
            )
            result = await db.execute(query)
            users = result.scalars().all()

        return total_count, [UserVO(**row_to_dict(user)) for user in users]

    async def find_by_email(self, email:str) -> UserVO:
        async with SessionLocal() as db:
            query = select(User).filter(User.email == email)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=422)

        return UserVO(**row_to_dict(user))

    async def find_by_id(self, id: int):
        async with SessionLocal() as db:
            query = select(User).filter(User.id == id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=422)

        return UserVO(**row_to_dict(user))

    async def update(self, user_vo: UserVO) -> UserVO:
        async with SessionLocal() as db:
            query = select(User).filter(User.id == user_vo.id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=422)

            user.name = user_vo.name
            user.password = user_vo.password

            db.add(user)
            await db.commit()

            return UserVO(**row_to_dict(user))
