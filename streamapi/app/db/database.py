from pymongo import MongoClient
from pymongo.results import InsertManyResult
from pymongo.database import Database
from typing import Union

from app.core.config import ATLAS_URI, DB_NAME
from app.models.task import TaskCreate, TaskRemove
from utils import Singleton

class DB(metaclass=Singleton):
    connection:Union[MongoClient,None] = None
    db:Union[Database, None] = None


    def __validate_proxies(self, proxy_list:list):
        form_proxies = [{'proxy_uri':proxy,'using':False,'active':True} for proxy in proxy_list]
        return form_proxies
    
    def __validate_tokens(self, tokens_list:list):
        form_tokens = [{'token':token,'using':False,'active':True} for token in tokens_list]
        return form_tokens

    def connect(self):
        if self.connection is None:
            self.connection = MongoClient(ATLAS_URI)
            self.db = self.connection[DB_NAME]

    def close(self):
        if self.connection is not None:
            self.connection.close()
        else:
            raise ValueError("DB connection doesn't exist")

    def create_api_key(self,api_key:str):
        ans = self.db['api_keys'].insert_one({'token':api_key})
        return ans 
    
    def check_api_key(self,api_key:str):
        ans = self.db['api_keys'].find_one({'token':api_key})
        if ans is not None:
            return ans['token']
        else:
            return None
    
    def load_proxies(self,proxy_list:list):
        form_list = self.__validate_proxies(proxy_list)
        result:InsertManyResult = self.db['proxies'].insert_many(form_list)
        if result.inserted_ids:
            return {"message": "Names inserted successfully"}
        else:
            return {"message": "Insertion failed"}

    def load_tokens(self, tokens_list:list):
        form_list = self.__validate_tokens(tokens_list)
        result:InsertManyResult = self.db['twitch_tokens'].insert_many(form_list)
        if result.inserted_ids:
            return {"message": "Names inserted successfully"}
        else:
            return {"message": "Insertion failed"}
    
    def get_proxy(self,):
        record = self.db['proxies'].find_one({'using':False,'active':True})
        return record['proxy_uri']

    def get_proxies(self,number):
        cursor = self.db['proxies'].find({'using':False,'active':True}).limit(number)
        records = [record['proxy_uri'] for record in cursor]
        return records

    def get_twitch_token(self,):
        record = self.db['twitch_tokens'].find_one({'using':False,'active':True})
        return record['token']

    def get_twitch_tokens(self,number):
        cursor = self.db['twitch_tokens'].find({'using':False,'active':True}).limit(number)
        records = [record['token'] for record in cursor]
        return records

    def deactivate_proxy(self, proxy):
        ans = self.db['proxies'].find_one_and_update({'proxy_uri':proxy},{"$set":{"active":False}})
        return ans
    
    def using_proxy(self, proxy):
        ans = self.db['proxies'].find_one_and_update({'proxy_uri':proxy},{"$set":{"using":True}})
        return ans
    
    def deactivate_token(self, token):
        ans = self.db['twitch_tokens'].find_one_and_update({'token':token},{"$set":{"active":False}})
        return ans

    def using_token(self, token):
        ans = self.db['twitch_tokens'].find_one_and_update({'token':token},{"$set":{"using":True}})
        return ans
    
    def create_task(self,task:TaskCreate):
        ans = self.db['tasks'].insert_one(task)
        return ans

    def remove_task(self,task:TaskRemove):
        ans = self.db['tasks'].delete_one(task)
        return ans