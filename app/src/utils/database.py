from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.config import get_settings

settings = get_settings()

DATABASE_URL = f"postgresql+asyncpg://{settings.database.username}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.name}"

# 비동기 엔진 및 세션 생성
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# 세션을 얻기 위한 종속성
async def get_db():
    async with SessionLocal() as session:
        yield session

# 데이터베이스 초기화 함수
async def init_db():
    from map.infra.db_models import branch, brand, room
    from user.infra.db_models import review, wishlist, user
    from map.infra.db_models import wishlist_has_room
    print("Importing models:", Base.metadata.tables.keys())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
