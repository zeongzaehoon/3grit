import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import BaseModel

class DatabaseSettings(BaseModel):
    host: str
    port: str
    username: str
    password: str
    name: str

class Settings(BaseSettings):
    database: DatabaseSettings
    jwt_secret: str
    
    model_config = {
        "env_file": None,
        "case_sensitive": False
    }
    
    # 환경 변수를 중첩된 모델 구조로 변환
    @classmethod
    def from_env(cls):
        return cls(
            database=DatabaseSettings(
                host=os.getenv("SQL_DB_HOST"),
                port=os.getenv("SQL_DB_PORT"),
                username=os.getenv("SQL_DB_USERNAME"),
                password=os.getenv("SQL_DB_PASSWORD"),
                name=os.getenv("SQL_DB_NAME")
            ),
            jwt_secret=os.getenv("JWT_SECRET")
        )

@lru_cache
def get_settings():
    return Settings.from_env()
