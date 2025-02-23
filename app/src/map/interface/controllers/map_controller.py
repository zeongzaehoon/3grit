from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from async_fastapi_jwt_auth import AuthJWT

from map.application.map_service import MapService
from .models import *
from utils.containers import Container
from dependency_injector.wiring import inject, Provide


map = APIRouter(prefix="/map")



@map.post("/register_store")
@inject
async def register_store(
    store: RegisterStoreBody,
	map_service: MapService = Depends(Provide[Container.map_service])
):
    register_store = await map_service.register_store(store)

    return register_store


# @map.put("/update_store")
# async def update_store(
#     store: UpdateStoreBody,
# 	map_service: MapService = Depends(Provide[MapContainer.map_service])
# ):
#     pass


# @map.delete("/delete_store")
# async def delete_store(
#     store: DeleteStoreBody,
# 	map_service: MapService = Depends(Provide[MapContainer.map_service])
# ):
#     pass

