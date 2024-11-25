import ast
import json

import tiktoken
# from pytz import timezone

from utils.constants import *
from utils.database.client.memory import RedisClient



def make_llmArgs(args:dict):
    """
    make llmArgs in order to seperated Action\n
    - pingpong_mode:bool -> indepth mode Y/n
    - redis_save:bool -> save conversation_history Y/n
    """
    args["insert_mongo"] = dict()
    if args.get("filename"):
        args["insert_mongo"]["filename"] = args["filename"]
    if args.get("info"):
        args["insert_mongo"] = {**args["insert_mongo"], **args["info"]}
    return args


def get_conversation_history(session_key, call:bool=None):
    """Redis에서 대화이력 가져오기"""
    count = RedisClient().get_number(session_key)
    if count == 0 and not call:
        conversations = []
    elif count > 40 and not call:
        conversations = RedisClient().get_history(session_key, -40, -1)
    else:
        conversations = RedisClient().get_history(session_key, 0, -1)
    
    if not call:
        conversation_history = [conversation for conversation in decode_data_from_redis(conversations)]
        return str(conversation_history)
    else:
        return decode_data_from_redis(conversations)


def redis_format(role, message):
    """Redis input data format"""
    form = {
        "message": message,
        "role": role,
    }
    return str(form)


def decode_data_from_redis(list_data):
    """
    레디스에서 가져온 데이터를 json으로 잘 전달해주기 위한 함수
    - 레디스 데이터는 리스트 내 문자 데이터로 구성
    - 리스트에서 문자 데이터("{key: value}") 하나하나 뽑아서 json으로 변경
    - 해당 데이터를 다시 리스트에 담아 리턴
    """
    if len(list_data) == 0:
        result = []
    else:
        result = list(map(lambda string_data: ast.literal_eval(string_data), list_data))
    return result


def get_pinecone_data(docs:list):
    results = []
    for document in docs:
        result = {}
        result['category'] = document.metadata.get('source', None)
        result['subject'] = document.metadata['chapter'] if document.metadata.get('chapter', None) else document.metadata.get('subject', None)
        result['content'] = document.metadata['text'] if document.metadata.get('text', False) else document.page_content
        result['url'] = document.metadata.get('url', None) if bool(document.metadata.get('isShow', False)) else None
        result['imageURL'] = document.metadata.get('imageURL', None)
        results.append(result)
    return results


def make_question_from_files(files):
    file_list = files.getlist('files')
    file_cnt = len(file_list)
    if file_cnt == 0:
        raise IndexError()
    elif file_cnt == 1:
        filename = files['files'].filename
        question = files['files'].read().decode('utf-8')
    else:
        question = list()
        filename = list()
        for file in file_list:
           data = file.read().decode('utf-8')
           data_json = json.loads(data)
           question.append(data_json)
           name = file.filename
           filename.append(name)
    return str(question), str(filename)


def get_token_size(context:str):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(context)
    return len(tokens)