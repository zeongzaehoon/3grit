import os
from pinecone import Pinecone
import openai, tiktoken
import numpy as np
from utils.constants import *



class PineconeClient:
    def __init__(self, api_key:str=None, index_name:str=None, model:str=None):
        self.api_key = api_key if api_key else os.getenv('PINECONE_API_KEY')
        self.index_name = index_name if index_name else MAIN_INDEX
        self.embed_model = model if model else EMBEDDING_MODEL
    
    def client(self):
        pc = Pinecone(api_key=self.api_key)
        return pc
    
    def index(self):
        #TODO@jaehoon: check get index, create index if not getting index
        if not self.index_name:
            index = self.client().Index(host=os.getenv("PINECONE_INDEX_HOST"))
        else:
            index = self.client().Index(name=self.index_name)
        return index
    
    def embedding(self, input):
        vector = openai.embeddings.create(
                    model="text-embedding-3-large",
                    input=input
        )
        return vector

    def embed(self, content, max:bool=None):
        if type(content) == str:
            vector = self.embedding(content)
            return vector.data[0].embedding
        elif type(content) == list and max:
            vectors = list()
            for c in content:
                tokens = self.make_tokens(c)
                if len(tokens) <= 8192:
                    vector = self.embedding(c)
                    vectors.append(vector.data[0].embedding)
                else:
                    words = c.split()
                    chunk_size = self.calculate_chunk_size(tokens)
                    chunk_datas = list(self.make_chunk(words, chunk_size))
                    chunk_vectors = list()
                    for chunk_data in chunk_datas:
                        chunk_vector = self.embedding(chunk_data)
                        chunk_vectors.append(chunk_vector.data[0].embedding)
                    vectors.append(np.mean(chunk_vectors, axis=0))
            return [v for v in vectors]
        else:
            vector = self.embedding(content)
            return [v.embedding for v in vector.data]
    
    def insert(self, id:str, content:str, metadata:dict, namespace:str=None):
        value = self.embed(content)
        vectors = [{"id": id, "values": value, 'metadata': metadata}]
        if namespace:
            self.index().upsert(vectors=vectors, namespace=namespace)
        else:
            self.index().upsert(vectors=vectors)

    def insert_many(self, ids:list, contents:list, metadatas:list, namespace:str=None):
        values = self.embed(contents)
        vectors = [{"id": id, "values": value, 'metadata': metadata} for id, value, metadata in zip(ids, values, metadatas)]
        if namespace:
            self.index().upsert(vectors=vectors, batch_size=32, namespace=namespace)    
        else:
            self.index().upsert(vectors=vectors, batch_size=32)            

    def remove(self, id:list=None, delete_all:bool=False, filter:dict=None):
        if id:
            self.index().delete(ids=id)
        elif id is None and filter is not None:
            self.index().delete(filter=filter) 

    def find(self, query:str=None, k:int=4, filter:dict=None):
        vector = self.embed(query) if query else None
        response = self.index().query(
            # namespace="example-namespace",
            vector=vector,
            top_k=k,
            include_values=False,
            include_metadata=True,
            filter=filter
        )
        return response['matches']

    def fetch(self, ids:list, namespace:str=None):
        if namespace:
            response = self.index().fetch(ids=ids, namespace=namespace)
        else:
            response = self.index().fetch(ids=ids)
        return response

    def make_chunk(self, words, size):
        for i in range(0, len(words), size):
            yield ' '.join(words[i:i + size])
    
    def make_tokens(self, words):
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(words)
        return tokens

    def calculate_chunk_size(self, tokens):
        return len(tokens) // EMBEDDING_MAX_TOKEN + 1