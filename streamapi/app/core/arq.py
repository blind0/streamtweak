import asyncio
from typing import Optional

from arq import create_pool
from arq.jobs import Job
from arq.connections import RedisSettings, ArqRedis

from app.core.config import REDIS_ARQ_HOST, REDIS_ARQ_PORT
from app.services.viewer_service.app import Application
from app.db.database import DB
from app.core.cache import Cache

from utils import Singleton

db = DB()
cache = Cache()
REDIS_ARQ_SETTINGS = RedisSettings(
    host=REDIS_ARQ_HOST,
    port=REDIS_ARQ_PORT,
    username='streamapi',
    password='streampulserootpassword',
)

class RedisPool(metaclass=Singleton):
    pool:Optional[ArqRedis] = None

    async def init_pool(self):
        self.pool = await create_pool(REDIS_ARQ_SETTINGS)
    
    async def close_pool(self):
        await self.pool.close()

    async def create_task(self,task_name:str,username, number):
        job = await self.pool.enqueue_job(task_name, username, number)
        return job

    async def get_task(self,task_id:str):
        job = Job(task_id,self.pool)
        return await job.info()


async def startup(ctx):
    db.connect()
    await cache.open()
    print('startup')

async def shutdown(ctx):
    db.close()
    await cache.close()
    print('shutdown')

async def start_twitch(ctx,username,number):
    print(username)
    app = Application(username=username,number=number)
    await app.run()

async def pingpong(ctx,):
    await ctx['redis'].ping()
