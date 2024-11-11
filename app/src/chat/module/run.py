import queue
import threading
import logging
import time
import ast

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain.schema.runnable import RunnablePassthrough
import tiktoken
from openai import RateLimitError

from .helper import *
from. model import *
from utils.constants import *
from utils.client.nosql import MongoClient
from utils.client.memory import RedisClient


def multiThread(runner, llmArgs):
    """Langchain-ChatGPT API로 질문주고 대답받음"""
    gen = ThreadedGenerator()
    threading.Thread(
        target=runner,
        args=(
            gen,
            llmArgs,
        ),
        daemon=True
    ).start()
    return gen


def make_systemPrompt_object(system_message:str, image_url:str=None):
    """chatGPT api에게 자신의 역할, 참고해야할 데이터 등을 넘기기 위한 문장구조 오브젝트 만듭니다"""
    from_message_args = [
        ("system", system_message),
        ("human", """human: {question}""")
    ]
    if image_url:
        url = {"image_url": {"url": image_url}, "type": "image_url"}
        human_message = [url]
        from_message_args.append(HumanMessage(content=human_message))
    
    prompt = ChatPromptTemplate.from_messages(from_message_args)
    return prompt


def run_multiThread():
    """chatGPT 셋팅: 멀티스레드 버전"""
    def chain_llm(gen, llmArgs):
        try:
            system_prompt = llmArgs["system_prompt"]           
            retrieval_data = llmArgs["retrieval_data"]
            retrieval_data_lambda = make_RunnableLambda(retrieval_data)
            question = llmArgs["question"]
            session_key =llmArgs["session_key"]
            indepth = llmArgs["indepth"]
            redis_save = llmArgs["redis_save"]
            s3_save = llmArgs.get("s3_save")
            capture_status = llmArgs.get("capture_status")
            docent_data = llmArgs.get("docent_data")
            docent_mode = llmArgs.get("docent_mode")
            # neccessary obejct: rag data & conversation history
            chain_objects = {
                "retrieval_data": retrieval_data_lambda,
                "question": RunnablePassthrough(),
            }
            token_dict = {"retrieval_data": retrieval_data, "question": question}
            
            if redis_save:
                conversation_history = llmArgs["conversation_history"]
                conversation_history_lambda = make_RunnableLambda(conversation_history)
                chain_objects['conversation_history'] = conversation_history_lambda
                token_dict['conversation_history'] = conversation_history
            
            if docent_mode:
                docent_history_list = ast.literal_eval(llmArgs["conversation_history"])
                docent_question = str([question for question in docent_history_list if question["role"] == "human"])
                docent_answer = str([question for question in docent_history_list if question["role"] == "ai"])
                chain_objects["before_question"] = make_RunnableLambda(docent_question)
                chain_objects["before_answer"] = make_RunnableLambda(docent_answer)
                token_dict['before_question'] = docent_question
                token_dict['before_answer'] = docent_answer

            if capture_status:
                llmArgs["capture_status"] = capture_image_checker(llmArgs["aireportId"])
            
            if not indepth:
                llmArgs["insert_mongo"]["token"] = get_token_size(system_prompt.format(**token_dict))
                data_mongo = mongo_format(session_key, "human", question, llmArgs["insert_mongo"])
                result = MongoClient().insert(data_mongo)
                llmArgs["insert_mongo"]["cid"] = str(result.inserted_id)                
                if redis_save:
                    data_redis = redis_format(role="human", message=question)
                    RedisClient().set_history(session_key, data_redis)
                    RedisClient().set_expire(session_key, 1800)                
                chain = chain_objects | system_prompt | llm(gen=gen, args=llmArgs)
                answer = chain.invoke(question)
                final_answer = answer.content
            else:
                all_answer = ""
                answer_list = []
                for order, p in enumerate(system_prompt):
                    llmArgs["insert_mongo"]["order"] = order+1
                    conversation_history = get_conversation_history(session_key)
                    token_dict['before_answer'] = all_answer
                    llmArgs["insert_mongo"]["token"] = get_token_size(p.format(**token_dict))
                    data_mongo = mongo_format(session_key, "human", question, llmArgs["insert_mongo"])
                    result = MongoClient().insert(data_mongo)
                    llmArgs["insert_mongo"]["cid"] = str(result.inserted_id)            
                    chain_objects['before_answer'] = make_RunnableLambda(all_answer)
                    chain = chain_objects | p | llm(gen=gen, args=llmArgs)
                    answer = chain.invoke(question)
                    all_answer = answer.content
                    answer_list.append(all_answer)
                    del llmArgs["insert_mongo"]["cid"]
                final_answer = '\n'.join(answer_list)
            
            if llmArgs['category'] == AIREPORT:
                question_data_redis = redis_format(role="human", message=question)
                RedisClient().set_history(session_key, question_data_redis)
                RedisClient().set_expire(session_key, 1800)
                answer_data_redis = redis_format(role="ai", message=final_answer)
                RedisClient().set_history(session_key, answer_data_redis)
                RedisClient().set_expire(session_key, 1800)
            
            if s3_save:
                save_s3(s3_save, final_answer)

        except RateLimitError as e:
            logging.info(f"[module][run.py][chain_llm] {e}")
            # send_slack_message(message=f"[solomon-api][noCredit] {e}🫠")
        except Exception as e:
            logging.info(e)
        finally:
            gen.close()
    return chain_llm



# ===========================================
# Background Class & Function
# ===========================================
class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration: raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


def get_retrieval_data(question, pinecone_index, refer:bool=None, k:int=4):
    """
    get Data For RAG \n\n
    - Data From Pinecone\n
    - return is different by refer(True, False)
    """
    index_name = pinecone_index if pinecone_index else MAIN_INDEX
    result = list() if refer else dict(retrieval_data=str(), rid=list())
    client = pinecone_client(index_name=index_name)
    if type(question) == list:
        fetchRes = client.fetch(question)
        docs = [doc for doc in fetchRes.vectors.values()]
    else:    
        docs = client.find(question, k)

    if refer:
        result += get_pinecone_data(docs)
    else:
        result["retrieval_data"] += format_docs(docs)
        result["rid"] += get_rid_list(docs)
    return result


def make_RunnableLambda(string_data:str):
    """
    ROLE
    ---
    RAG에서 사용할 데이터 LAMBDA 함수 생성
    """
    return RunnableLambda(lambda x: string_data)


def get_combined_context(retrieval_data, conversation_history):
    """
    vector화된 데이터를 질문에 매칭시키기 위한 함수
    ***langchain.schema.runnable.RunnableLambda로 적용
    """
    combined_context = RunnableLambda(lambda x: combine_context_and_docs(retrieval_data, conversation_history))
    return combined_context


def get_token_size(context:str):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(context)
    return len(tokens)