from utils.database.alchemy import engine, Base

# 데이터베이스 초기화 함수
async def init_db():
    async with engine.begin() as conn:
        # 테이블 생성
        await conn.run_sync(Base.metadata.create_all)