from dataclasses import dataclass
from datetime import datetime

@dataclass
class Profile:
    """_summary_
        이렇게 Profile을 별도의 도메인으로 분리했다고 해서 데이터베이스도 분리해 Profile 테이블을 만들 필요는 없다.
        Profile에는 id 속성이 없다. 이처럼 데이터만 가지고 있는 도메인 객체를 값 객체(Value Object)라고 한다.
    """
    name: str
    email: str

@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime
