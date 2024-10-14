import os

# MODEL_LIST
BASE_MODEL = "gpt-4o"
GEMINI_MODEL_LIST = ["gemini-1.5-pro-0125"]
CLAUDE_MODEL_LIST = ["claude-3-opus-20240229", "claude-3-haiku-20240307", "claude-3-sonnet-20240229"]
CHATGPT_MODEL_LIST = ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"]
MODEL_LIST = GEMINI_MODEL_LIST + CLAUDE_MODEL_LIST + CHATGPT_MODEL_LIST

# PINECONE INDEX CONSTANTS
MAIN_INDEX = "solomon-main"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_TIKTOKEN_MODEL = "cl100k_base"
EMBEDDING_MAX_TOKEN = 8192

# THE PROMPT OF CONV HISTORY
CONVERSATION_HISTORY = """
    아래는 당신과 사용자 간의 이전 대화 내용입니다.
    이전 대화 내용 맥락을 읽고 사용자의 질문에 대해 자세히 알려주세요.
    단, 가장 중요한건 사용자가 현재한 질문 내용입니다. 이 전에 같은 질문을 했다면 만족하지 못하고 다시 질문한 것일 수 있으니 이전 대화이력에 있는 대답을 똑같이 하지말고 다시 한번 생각해 대답해주시길 바랍니다.
    이전 대화 이력: {conversation_history}
    """