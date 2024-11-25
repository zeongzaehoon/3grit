# default lib
import os
# from dotenv import load_dotenv
from uuid import uuid4

# fast-api
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

# router
from chat.chat import chat
from map.map import map
# from src.user.user import user

# server
import uvicorn

# database - alchemy
from utils.database import init_db

# api setting
app = FastAPI()
app.include_router(chat)
app.include_router(map)
# app.include_router(user)

#init database
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
