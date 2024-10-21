# python inner 
import logging

# fastapi
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import JWTDecodeError

# model
from .payload import *

# llm module
from .module.langchain import RunLLM

# helper
from .helper import *



chat = APIRouter(prefix="/chat")



@chat.post("/run")
async def run(payload: ChatPayload, Authorize: AuthJWT = Depends()):
    try:
       identity = Authorize.jwt_required()
    except JWTDecodeError:  # AuthJWTException 대신 JWTDecodeError 사용
        raise HTTPException(status_code=401, detail="Invalid token")    
    
    user_id = identity.get("user_id")
    question = payload.question
    return StreamingResponse(RunLLM(question, user_id), media_type="text/plain")


@chat.get("/history")
async def history(Authorize: AuthJWT = Depends()):
    try:
       identity = Authorize.jwt_required()
    except JWTDecodeError:  # 여기도 마찬가지로 변경
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = identity.get("user_id")
    conversation_history = RunLLM(args={"redis_key": user_id}).get_conversation_history(call=True)
    return JSONResponse(status_code=200, content={"message": "success", "data": conversation_history})
