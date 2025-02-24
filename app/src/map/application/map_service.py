from datetime import datetime
from pytz import timezone
from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException, Depends, status
from typing import Annotated
from map.domain.store import Store
from map.domain.repository.map_repo import IMapRepository
from map.infra.repository.map_repo import MapRepository


class MapService:
    @inject
    def __init__(
        self,
        map_repo: IMapRepository,
    ):
        self.map_repo = map_repo

    async def register_store(self, store):
        current_time = datetime.now(timezone('UTC'))
        
        store: Store = Store(
            category_id=store.CategoryId,
            subcategory_id=store.SubCategoryId,
            name=store.Name,
            mapx=store.MapX,
            mapy=store.MapY,
            created_date=current_time,
            updated_date=current_time,
            address_name=store.AddressName,
            kakao_map_id=store.KakaoMapId,
        )
        
        await self.map_repo.register(store)


    async def get_map(self, kakao_map_id: str):
        pass
