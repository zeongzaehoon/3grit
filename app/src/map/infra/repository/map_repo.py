from utils.database import SessionLocal
from map.domain.repository.map_repo import IMapRepository
from map.domain.store import Store as StoreVO
from map.infra.db_models.store import Store
from fastapi import HTTPException
from sqlalchemy import select, func
from utils.helpers import row_to_dict



class MapRepository(IMapRepository):
    async def register(self, store:StoreVO):
        new_store = Store(
            category_id=store.category_id,
            subcategory_id=store.subcategory_id,
            name=store.name,
            mapx=store.mapx,
            mapy=store.mapy,
            address_name=store.address_name,
            kakao_map_id=store.kakao_map_id,
            created_date=store.created_date,
            updated_date=store.updated_date,
        )

        async with SessionLocal() as db:
            db.add(new_store)
            await db.commit()