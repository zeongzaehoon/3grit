import os
import pymongo



class MongoClient:
    def __init__(self, host:str=None, port:int=None, username:str=None, password:str=None, database:str=None, collection:str=None):
        self.host = host or os.getenv("NOSQL_DB_HOST")
        self.port = port or os.getenv("NOSQL_DB_PORT")
        self.username = username or os.getenv("NOSQL_DB_USERNAME")
        self.password = password or os.getenv("NOSQL_DB_PASSWORD")
        self.database = database or os.getenv("NOSQL_DB_NAME")
        self.collection = collection or os.getenv('NOSQL_DB_COLL_NAME')

    def client(self):
        client = pymongo.MongoClient(
            host=self.host,
            port=int(self.port),
            username=self.username,
            password=self.password)
        return client

    def db(self):
        db = self.client().get_database(self.database)
        return db

    def coll(self):
        collection_list = self.db().list_collection_names()
        if self.collection not in collection_list:
            self.db().create_collection(self.collection)
        coll = self.db().get_collection(self.collection)
        return coll

    def insert(self, data):
        return self.coll().insert_one(data)

    def update_one(self, query:dict, update:dict):
        update_query = {'$set': update}
        self.coll().update_one(query, update_query)

    def update_many(self, query:dict, update:dict):
        update_query = {'$set': update}
        self.coll().update_many(query, update_query)

    def find(self, **kwargs: dict):
        query = kwargs.get('query')
        sort = kwargs.get('sort', None)
        skip = kwargs.get('skip', None)
        limit = kwargs.get('limit', None)
        if sort and skip and limit:
            return self.coll().find(query).sort(sort).skip(skip).limit(limit)
        elif sort and skip:
            return self.coll().find(query).sort(sort).skip(skip)
        elif sort and limit:
            return self.coll().find(query).sort(sort).limit(limit)
        elif skip and limit:
            return self.coll().find(query).skip(skip).limit(limit)
        elif sort:
            return self.coll().find(query).sort(sort)
        elif skip:
            return self.coll().find(query).skip(skip)
        elif limit:
            return self.coll().find(query).limit(limit)
        else:
            return self.coll().find(query)
    
    def find_one(self, **kwargs):
        query = kwargs.get('query')
        sort = kwargs.get('sort', None)
        if sort:
            return self.coll().find_one(filter=query, sort=sort)
        else:
            return self.coll().find_one(filter=query)
        
    def distinct(self, field:str, query:dict):
        return self.coll().distinct(field, query)