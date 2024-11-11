import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = f"postgresql://{os.getenv('SQL_DB_USERNAME')}:{os.getenv('SQL_DB_PASSWORD')}@{os.getenv('SQL_DB_HOST')}:{os.getenv('SQL_DB_PORT')}/{os.getenv('SQL_DB_NAME')}"

# 비동기 엔진 및 세션 생성
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# 세션을 얻기 위한 종속성
async def get_db():
    async with SessionLocal() as session:
        yield session