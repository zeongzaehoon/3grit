from dataclasses import dataclass
from datetime import datetime
from typing import Optional



@dataclass
class Store:
    name: str
    mapx: float
    mapy: float
    address_name: str
    created_date: datetime
    updated_date: datetime
    kakao_map_id: int

    store_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None