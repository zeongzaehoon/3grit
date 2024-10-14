from uuid import uuid4
import os
import logging

from .run import *
from .helper import *
from .model import *

from utils.constants import *



class RunLLM:
    # explain role, type, params
    """
    ROLE
    ---
    MODULE for RUNNING LLM

    CALL
    ---
    RunLLM(args, model, thread, dummy).execute()\n\n
    if call from 'api' -> retrun Response(RunLLM(args, thread, True, dummy).execute())\n
    if call from 'message queue consumer' -> RunLLM(args, thread, False, dummy).execute()
    
    PARAMS TYPE
    ---
    args: dict -> neccessary parameter
    thread: bool -> optional parameter
    stream: bool -> optional parameter
    dummy: bool -> optional parameter

    args sample
    ---
    {
        "session_key": str(uuid4()),\n
        "question": "{type: trend, ...}",\n
        "category": "aireport",\n
        "info_eagle": {"email": "jaehoon@4grit.com", ...},\n
        "filename": "uploadFile.json",\n
        "model": "gpt-4o"
    }
    """

    def __init__(self, args:dict, thread:bool=None, stream:bool=None, dummy:bool=None):
        self.args = args
        self.thread = thread if thread is not None else True
        self.stream = stream if stream is not None else True
        self.args["streaming"] = self.stream
        self.dummy = dummy if dummy is not None else bool(os.getenv("DOCKER"))


    def execute(self):
        self._get_llmArgs()
        self._get_query()
        self.get_retrieval_data()
        self.get_conversation_history()
        self._get_prompt()
        self._transform_object()
        self._get_model()
        return self._run()


    def _run(self):
        # not multi-thread
        if not self.thread and not self.dummy:
            logging.info("run_singleThread")
            return run_singleThread(self.llmArgs)
        # dummy-api
        elif self.dummy:
            logging.info("run_dummy")
            return run_dummy(self.llmArgs)
        # multi-thread
        else:
            logging.info("run_multiThread")
            return multiThread(
                    run_multiThread(),
                    self.llmArgs,
                )


    def _get_llmArgs(self):
        if not self.args or not isinstance(self.args, dict):
            raise ValueError("params is required and must be dict")

        self.llmArgs = make_llmArgs(self.args)


    def _get_query(self):
        category = self.llmArgs.get("category")
        self.query_prompt, qid = get_query_prompt(category, self.llmArgs.get("question"))
        self.llmArgs["insert_mongo"]["qid"] = qid


    def get_retrieval_data(self, call:bool=None):
        if call:
            refer=True
            return get_retrieval_data(self.args["question"], MAIN_INDEX, refer=refer, k=4)
        else:
            retrieval_result = get_retrieval_data(self.query_prompt, MAIN_INDEX, k=4)
            self.llmArgs["retrieval_data"] = retrieval_result["retrieval_data"]
            self.llmArgs["insert_mongo"]["rid"] = retrieval_result["rid"]


    def get_conversation_history(self, call:bool=None):
        if call:
            return get_conversation_history(self.args["session_key"], call)
        else:
            self.llmArgs["conversation_history"] = get_conversation_history(self.args["session_key"])
    
    # TODO@jaehoon: should do Clean!
    def _get_prompt(self):
        if not self.llmArgs or not isinstance(self.llmArgs, dict):
            raise ValueError("llmArgs is required and must be dict")
        
        category = self.llmArgs.get("category")
        roleNameList = self.llmArgs.get("roleNameList", None)
        roleNameListForPlus = self.llmArgs.get("roleNameListForPlus", None)
        # GET PROMPT FROM MONGO
        self.prompt, pid = get_system_prompt(category, roleNameList, roleNameListForPlus)
        self.llmArgs["insert_mongo"]["pid"] = pid
        self.llmArgs["insert_mongo"]["category"] = category
        if self.llmArgs["redis_save"]:
            self.prompt = self.prompt + '\n\n' + CONVERSATION_HISTORY


    def _transform_object(self):
        if self.llmArgs.get("category") not in SERVICE_LIST:
            raise ValueError("category is required and must be in SERVICE_LIST")
        if not self.llmArgs or not isinstance(self.llmArgs, dict):
            raise ValueError("args is required and must be dict")

        if self.llmArgs.get("indepth"):
            self.llmArgs["system_prompt"] = [make_systemPrompt_object(sep_system_message) for sep_system_message in self.prompt]
            self.llmArgs["insert_mongo"]["tid"] = str(uuid4())
        else:
            self.llmArgs["system_prompt"] = make_systemPrompt_object(self.prompt)


    def _get_model(self):
        if self.dummy:
            logging.info("Dummy model is selected")
            self.llmArgs["insert_mongo"]["model"] = "dummy"
            self.llm = "dummy"
        else:
            if not self.llmArgs.get("model", None):
                logging.info("model is not selected. Use BASE_MODEL")
                self.llmArgs["model"] = BASE_MODEL
            self.llmArgs["insert_mongo"]["model"] = self.llmArgs["model"]