import os
import redis



class RedisClient:
    def __init__(self, host=None, port=None, db=None):
        self.host = host or os.getenv('SESSION_STORAGE_HOST')
        self.port = port or os.getenv('SESSION_STORAGE_PORT')
        self.db = db or os.getenv('SESSION_STORAGE_DB_NUMBER')

    def client(self):
        client = redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=True,
            db=self.db)
        return client

    def set_history(self, key: str, value: str):
        self.client().rpush(key, value)

    def set_expire(self, key: str, time: int):
        self.client().expire(key, time)

    def get_number(self, key: str):
        return self.client().llen(key)

    def get_history(self, key: str, start=0, end=-1):
        return self.client().lrange(key, start, end)

    def get_session_key(self):
        return self.client().keys()

    def delete_session_key_data(self, key):
        self.client().delete(key)