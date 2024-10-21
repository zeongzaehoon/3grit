import time
from bson.objectid import ObjectId

from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler

from client.memory import RedisClient
from utils.constants import *

from .helper import *



def llm(gen, args):
    model = args["model"] if args.get("model", None) else BASE_MODEL
    
    if args["streaming"]:
        if gen:
            callbacks = [StreamingMultiThreadHandler(gen, args)]
        else:
            callbacks = [StreamingSingleThreadHandler(args)]
    else:
        if gen:
            callbacks = [AIReportMultiThreadHandler(gen, args)]
        else:
            callbacks = [AIReportSingleThreadHandler(args)]

    if model in CHATGPT_MODEL_LIST:
        result = ChatOpenAI(
            model_name = model,
            verbose=True,
            streaming=True,
            callbacks=callbacks,
            temperature=0.2
        )
    
    return result



class StreamingMultiThreadHandler(StreamingStdOutCallbackHandler):
    """langchain Streaming Multi Thread 콜백 클래스"""
    message = ""
    def __init__(self, gen, args):
        super().__init__()
        self.gen = gen
        self.indepth = args.get("indepth", None)
        self.insert_mongo = args.get("insert_mongo", None)
        self.session_key = args.get("session_key", None)
        self.redis_save = args.get("redis_save", True)
        self.capture_status = args.get("capture_status", None)
        self.docent_mode = args.get("docent_mode", None)

    def on_llm_end(self, *args, **kwargs):
        if self.capture_status and not self.docent_mode:
            for interval in len(range(0, 5)):
                time.sleep(1)
                result = capture_image_checker(args["aireportId"])
                if not result:
                    break
        save_id(self.session_key, self.message, self.insert_mongo, self.indepth)
        if self.redis_save:
            data_redis = redis_format(role="ai", message=self.message)
            RedisClient().set_history(self.session_key, data_redis)
            RedisClient().set_expire(self.session_key, 1800)

    def on_llm_new_token(self, token:str, **kwargs):
        self.message += token
        self.gen.send(token)


class StreamingSingleThreadHandler(StreamingStdOutCallbackHandler):
    """langchain Streaming Single Thread 콜백 클래스"""
    message = ""
    def __init__(self, args):
        super().__init__()
        self.indepth = args.get("indepth")
        self.session_key = args.get("session_key")
        self.insert_mongo = args.get("insert_mongo")
        self.redis_save = args.get("redis_save")
        

    def on_llm_end(self, *args, **kwargs):
        save_id(self.session_key, self.message, self.insert_mongo, self.indepth)
        if self.redis_save:
            data_redis = redis_format(role="ai", message=self.message)
            RedisClient().set_history(self.session_key, data_redis)
            RedisClient().set_expire(self.session_key, 1800)

    def on_llm_new_token(self, token:str, **kwargs):
        self.message += token


class AIReportMultiThreadHandler(BaseCallbackHandler):
    """langchain Streaming Multi Thread 콜백 클래스"""
    message = ""
    def __init__(self, gen, args):
        super().__init__()
        self.gen = gen
        self.indepth = args.get("indepth", None)
        self.insert_mongo = args.get("insert_mongo", None)
        self.session_key = args.get("session_key", None)
        self.redis_save = args.get("redis_save", True)

    def on_llm_end(self, *args, **kwargs):
        save_id(self.session_key, self.message, self.insert_mongo, self.indepth)
        if self.redis_save:
            data_redis = redis_format(role="ai", message=self.message)
            RedisClient().set_history(self.session_key, data_redis)
            RedisClient().set_expire(self.session_key, 1800)

        mongo_client(collection='baAIReport').update_one(query={'_id': ObjectId(self.session_key)}, update={'$set': {'getResult': True}}) # sample code

    def on_llm_new_token(self, token:str, **kwargs):
        self.message += token
        self.gen.send(token)


class AIReportSingleThreadHandler(BaseCallbackHandler):
    """langchain Streaming Single Thread 콜백 클래스"""
    message = ""
    def __init__(self, args):
        super().__init__()
        self.indepth = args.get("indepth", None)
        self.session_key = args.get("session_key", None)
        self.insert_mongo = args.get("insert_mongo", None)
        self.redis_save = args.get("redis_save", None)

    def on_llm_end(self, *args, **kwargs):
        save_id(self.session_key, self.message, self.insert_mongo, self.indepth)
        if self.redis_save:
            data_redis = redis_format(role="ai", message=self.message)
            RedisClient().set_history(self.session_key, data_redis)
            RedisClient().set_expire(self.session_key, 1800)

    def on_llm_new_token(self, token:str, **kwargs):
        self.message += token