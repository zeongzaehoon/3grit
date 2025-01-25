# default lib
import os
# from dotenv import load_dotenv
from uuid import uuid4

# fast-api
from utils.containers import Container
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

# router
from chat.chat import chat
from map.map import map
from user.interface.controllers.user_controller import router as user_routers
# from src.user.user import user

# server
import uvicorn

# database - alchemy
from utils.database import init_db

# api setting
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.container = Container()
app.container.wire(modules=["user.interface.controllers.user_controller"])

app.include_router(chat)
app.include_router(map)
app.include_router(user_routers)


# init database
@app.on_event("startup")
async def on_startup():
    await init_db()

# AuthJWT configuration settings
class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv('JWT_SECRET_KEY', 'BE-EAGLE SECRET')

@AuthJWT.load_config
def get_config():
    return Settings()

# Exception handlers
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# API for token
@app.get("/check")
async def _check():
    return {"code": 200, "message": "I AM LIVING", "data": ""}


@app.get("/hello")
async def _hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        return {"code": 200, "message": "hello", "data": ""}
    except AuthJWTException:
        identify = str(uuid4())
        access_token = Authorize.create_access_token(subject=identify)
        refresh_token = Authorize.create_refresh_token(subject=identify)
        return {"code": 200, "message": "hello", "data": "", "access_token": access_token, "refresh_token": refresh_token}


@app.get("/refresh")
async def _refresh(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user)
    return {"code": 200, "message": "refresh", "data": "", "access_token": access_token}


# Run API server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
