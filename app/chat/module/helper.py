import os
import ast
import json
import logging

from bson import ObjectId
import requests
import tiktoken
from datetime import datetime, timezone
import pytz

from utils.constants import *
from client.nosql import MongoClient
from client.memory import RedisClient



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


def get_system_prompt(category:str, roleNameList:list[str], roleNameListForPlus:list[str]):
    """
    get prompt from mongo
    """
    prompt_category = get_prompt_category(category)
    if roleNameListForPlus:
        # base prompt 추출
        module_prompts = list()
        base_pid = list()
        for enum, roleName in enumerate(roleNameList):
            if  roleName != PINGPONG_INDEX:
                prompt_result = get_prompt_from_mongo(category=prompt_category, kind="prompt", roleName=roleName)
                module_prompts.append(prompt_result[1])
                base_pid.append(str(prompt_result[0]))
            else:
                pingpong_placeholder = PINGPONG_INDEX
                module_prompts.append(pingpong_placeholder)
                base_pid.append(PINGPONG_INDEX)
                pingpongPrompts_index = enum
        # pingpong prompt 추출 후 base prompt에 넣기
        prompt = list()
        pid = list()
        for pingpong_roleName in roleNameListForPlus:
            pingpong_prompt_result = get_prompt_from_mongo(category=prompt_category, kind="prompt", roleName=pingpong_roleName)
            module_prompts[pingpongPrompts_index] = pingpong_prompt_result[1]
            base_prompt = '\n\n'.join(module_prompts)
            base_pid[pingpongPrompts_index] = str(pingpong_prompt_result[0])
            prompt.append(base_prompt)
            pid.append(base_pid)        
    # 이 외
    else:
        if roleNameList:
            modulePrompts = list()
            pid = list()
            for roleName in roleNameList:
                prompt_result = get_prompt_from_mongo(category=prompt_category, roleName=roleName)
                modulePrompts.append(prompt_result[1])
                pid.append(str(prompt_result[0]))
            prompt = "\n\n".join(modulePrompts)
        else:
            prompt_result = get_prompt_from_mongo(category=prompt_category)
            prompt = prompt_result[1]
            pid = str(prompt_result[0])
    return prompt, pid


def get_query_prompt(category, question=None):
    prompt_category = get_prompt_category(category)
    if category in QUERY_CATEGORY_PROMPT_LIST:
        query_result = get_prompt_from_mongo(category=prompt_category, kind="query")
        pinecone_query = ast.literal_eval(query_result[1]) if query_result[1][0] == '[' and query_result[1][-1] == ']' else query_result[1]
        qid = str(query_result[0])
    else:
        pinecone_query = question
        qid = None
    return pinecone_query, qid


def get_prompt_from_mongo(**kwargs:dict):
    query = kwargs
    sort = [("date", -1)] #{"date": -1}
    collection = os.getenv("DB_PROMPT_COLL_NAME") #"solomonPromptHistory"
    mongo = MongoClient(collection=collection)
    result = mongo.find_one(query=query, sort=sort)
    return [result["_id"], result["prompt"]]


def get_prompt_category(category):
    if category in UXGPT_LIST:
        prompt_category = CS
    elif category in SWCAG_LIST:
        prompt_category = SWCAG
    else:
        prompt_category = category
    return prompt_category


def get_conversation_history(session_key, call:bool=None):
    """Redis에서 대화이력 가져오기"""
    count = redis_client().get_number(session_key)
    if count == 0 and not call:
        # conversations = ['{"message": "It`s first", "role":"ai"}']
        conversations = ''
    elif count > 40 and not call:
        conversations = redis_client().get_history(session_key, -40, -1)
    else:
        conversations = redis_client().get_history(session_key, 0, -1)
    
    if not call:
        conversation_history = [conversation for conversation in decode_data_from_redis(conversations)]
        return str(conversation_history)
    else:
        return decode_data_from_redis(conversations)


def combine_context_and_docs(retrieval_data, conversation_history):
    """
    사용자 대화 이력 데이터 + 사용자 질문에 적합한 데이터
    """
    result = f"\n\n--- Below are the contents from the result of retrieval from VectorDB ---\n\n{retrieval_data}\n\n--- Below are the conversation history data from InMemory DB ---\n\n{conversation_history}"
    return result


def format_docs(docs):
    documents = list()
    for document in docs:
        imageURL = document.metadata['imageUrl'] if document.metadata.get('imageUrl', None) else document.metadata.get('imageURL', None)
        isShow = bool(document.metadata.get('isShow', False))
        if imageURL and isShow:
            page_content = {"content": document.metadata.get('text',''), "imageURL": imageURL}
        else:
            page_content = {"content": document.metadata.get('text', '')}
        documents.append(page_content)

    return str(documents)


def get_rid_list(docs):
    return [document['id'] for document in docs]


def mongo_format(session_key, role, message, extra:dict=None):
    """몽고 DB input data format"""
    form = {
        "sessionKey": session_key,
        "role": role,
        "message": message,
        "date": datetime.now(timezone.utc),
        "rating":0
    }
    if extra:
        form = {**form, **extra}
    return form


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


def get_base_url():
    base_url = None
    if os.getenv("DOCKER"):
        base_url = BASE_URL_DOCKER_DEV
    elif os.getenv("FLASK_CONFIG") == "local-development" or os.getenv("FLASK_CONFIG") == "development":
        base_url = BASE_URL_DEV
    elif os.getenv("FLASK_CONFIG") == "staging":
        base_url = BASE_URL_STAGING
    elif os.getenv("FLASK_CONFIG") == "production":
        base_url = BASE_URL_PRODUCTION
    return base_url


def save_id(session_key, message, insert_mongo, indepth):
    insert_mongo["token"] = get_token_size(message)
    data_mongo = mongo_format(session_key, "ai", message, insert_mongo)
    MongoClient().insert(data_mongo)
    pid = insert_mongo.get("pid", None)
    qid = insert_mongo.get("qid", None)
    if pid and type(pid) == str:
        query = {'_id': ObjectId(pid)}
        update = {'getResult': True}
        MongoClient(collection=os.getenv('DB_PROMPT_COLL_NAME')).update_one(query=query, update=update)
    elif pid and type(pid) == list:
        if indepth:
            pids = [pid for sublist in pid for pid in sublist]
            for pid in pids:
                query = {'_id': ObjectId(pid)}
                update = {'getResult': True}
                MongoClient(collection=os.getenv('DB_PROMPT_COLL_NAME')).update_one(query=query, update=update)        
        else:
            for pid in pid:
                query = {'_id': ObjectId(pid)}
                update = {'getResult': True}
                MongoClient(collection=os.getenv('DB_PROMPT_COLL_NAME')).update_one(query=query, update=update)
    if qid and type(qid) == str:
        query = {'_id': ObjectId(qid)}
        update = {'getResult': True}
        MongoClient(collection=os.getenv('DB_PROMPT_COLL_NAME')).update_one(query=query, update=update)
    elif qid and type(qid) == list:
        if indepth:
            qids = [qid for sublist in qid for qid in sublist]
            for qid in qids:
                query = {'_id': ObjectId(qid)}
                update = {'getResult': True}
                MongoClient(collection=os.getenv('DB_PROMPT_COLL_NAME')).update_one(query=query, update=update)
        else:
            for qid in qid:
                query = {'_id': ObjectId(qid)}
                update = {'getResult': True}
                MongoClient(collection=os.getenv('DB_PROMPT_COLL_NAME')).update_one(query=query, update=update)


def save_s3(s3_save:dict, data:str):
    aireport_id = s3_save['id']
    type_ = s3_save['type']
    parent_sid = s3_save['parentSid']
    reg_date = s3_save['regDate']
    start = s3_save['startDateStr']
    end = s3_save['endDateStr']
    start_format = start.replace('-', '')[2:]
    end_format = end.replace('-', '')[2:]
    file_name = f'{parent_sid}_{type_}_{start_format}_{end_format}_report.txt'
    s3_path = f'journeymap/{reg_date}/{parent_sid}/{aireport_id}/{file_name}'
    s3_client = get_boto3_client()
    s3_client.put_object(Bucket=AWS_BUCKET_NAME, Key=s3_path, Body=json.dumps(data, ensure_ascii=False))
    baAIReport = MongoClient(collection='baAIReport')
    query={"_id":ObjectId(aireport_id)}
    update={
        "reportDate": pytz.timezone('Asia/Seoul').localize(datetime.now()),
        "reportStatus": "complete",
        "reportS3Path": f"{AWS_BUCKET_NAME}:{s3_path}"
    }
    baAIReport.update_one(query=query, update=update)


def capture_image_checker(id):
    baAIReport = MongoClient(collection="baAIReport")
    query = {"_id": ObjectId(id)}
    cursor = baAIReport.find_one(query=query)
    analysis_type = cursor["type"]
    capture_status = cursor["captureStatus"]
    capture_s3_path = cursor["captureS3Path"]
    if capture_status == "complete" and capture_s3_path:
        logging.info(f"===========capture_image_checker: capture is completed and new row({id}) already has capture.")
        return False
    else:
        ref_aid = str(cursor["refAid"][0])
        query_original = {"_id": ObjectId(ref_aid)}
        cursor_original = baAIReport.find_one(query=query_original)
        analysis_type_original = cursor_original["type"] 
        capture_list = cursor_original.get("captureList")
        capture_count = cursor_original.get("captureCount")
        capture_status_original = cursor_original["captureStatus"]
        capture_s3_path_original = cursor_original["captureS3Path"]

        # 데이터가 꼬여있으면 그냥 넘어가. 대신 로그를 남겨두자.
        if analysis_type != analysis_type:
            logging.info(f"===========capture_image_checker: original type: {ref_aid} and new row type: {id} are diffrent. check it!")
            return True
        if not capture_count or not capture_list:
            logging.info(f"===========capture_image_checker: _id={ref_aid}, original captureList or original captureCount is None. check it!")
            return True
        if analysis_type_original == AIREPORT_TYPE_JOURNEY:
            if capture_status_original == 'complete' and capture_count == 4:
                major = capture_list.get("major")
                rollback = capture_list.get("rollback")
                reload = capture_list.get("reload")
                drop = capture_list.get("drop")
                if major and rollback and reload and drop and len(major) > 0 and len(major) > 0 and len(major) > 0 and len(major) > 0:
                    query ={"_id": ObjectId(id)}
                    update = {"captureStatus": "complete", "captureS3Path": capture_s3_path_original}
                    baAIReport.update_one(query=query, update=update)
                    return False
            else:
                logging.info(f"===========capture_image_checker: _id={ref_aid} capture is complete. check it!")
                return True
        elif analysis_type_original == AIREPORT_TYPE_TREND or analysis_type_original == AIREPORT_TYPE_JOURNEY:
            if capture_status_original == 'complete' and capture_count == 1:
                all = capture_list.get("all")
                if all and len(all) > 0:
                    query ={"_id": ObjectId(id)}
                    update = {"captureStatus": "complete", "captureS3Path": capture_s3_path_original}
                    baAIReport.update_one(query=query, update=update)
                    return False
            else:
                logging.info(f"===========capture_image_checker: _id={ref_aid} capture is complete. check it!")
                return True


def get_token_size(context:str):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(context)
    return len(tokens)


def send_slack_message(message, channel=None):
    SLACK_API_URL = 'https://slack.com/api/chat.postMessage'
    msg_obj = {
        'channel': '#alert' if channel is None else channel,
        'text': message
    }
    header = {
        'Authorization': 'Bearer {}'.format(os.getenv('SLACK_TOKEN')),
        'Content-Type': 'application/json'
    }
    try:
        res = requests.post(SLACK_API_URL, json=msg_obj, headers=header)
        logging.info('res: {}'.format(res.json()))
        return res
    except Exception as e:
        logging.error(e)