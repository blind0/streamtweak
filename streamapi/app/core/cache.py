from aiocache.plugins import BasePlugin
from aiocache import SimpleMemoryCache

from typing import Optional
import time

from utils import Singleton


class TimestampExpiryPlugin(BasePlugin):
    async def post_get(self,client,key,ret,*args,**kwargs):
        value, expiration_timestamp = ret
        if time.time() >= expiration_timestamp:
            await client.delete(key)
            return None
        return value


class Cache(metaclass=Singleton):
    cache:Optional[SimpleMemoryCache] = None

    async def open(self):
        self.cache = SimpleMemoryCache(plugins=[TimestampExpiryPlugin()])
    
    async def close(self):
        await self.cache.close()

    async def set_timestamp_cache(self,key, value, expiration_timestamp):
        await self.cache.set(key, (value, expiration_timestamp))

    async def get_timestamp_cache(self,key):
        if not await self.cache.exists(key):
            return False
        return await self.cache.get(key)
    
