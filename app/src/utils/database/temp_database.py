# SQLAlchemy의 핵심 기능들을 가져옵니다
from sqlalchemy import create_engine

# SQLAlchemy ORM의 선언적 모델링을 위한 기본 클래스를 가져옵니다
from sqlalchemy.ext.declarative import declarative_base

# 데이터베이스 세션 관리를 위한 sessionmaker를 가져옵니다
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스의 URL을 정의합니다. 현재 디렉토리에 test.db 파일을 생성합니다
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:test@localhost:3306/fastapi-ca"

# 데이터베이스 엔진을 생성합니다
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 데이터베이스 세션 팩토리를 생성합니다
# autocommit=False: 자동 커밋을 비활성화
# autoflush=False: 자동 플러시를 비활성화
# bind=engine: 생성한 엔진과 세션을 연결
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 모델들이 상속받을 기본 클래스를 생성합니다
Base = declarative_base()
