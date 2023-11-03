from fastapi import APIRouter, Depends, Security, Body
from fastapi.encoders import jsonable_encoder
from arq.jobs import Job

from app.core.auth import get_master_api_key, get_api_key
from app.core.arq import RedisPool
from app.api.api import get_token
from app.db.database import DB
from app.models.task import TaskCreate, TaskRemove, TaskStatus, TaskPause

router = APIRouter()
db = DB()
redis_pool = RedisPool()

@router.post("/task/add")
async def task_add(api_key:str = Security(get_api_key),task:TaskCreate = Body(...)) -> dict[str,str]:
    task = jsonable_encoder(task)
    print(task)
    db.create_task(task)
    job:Job = await redis_pool.create_task(task_name='start_twitch',username=task.get('channel_name'),number=task.get('viewer_number'))
    return {'task_id':f'{task.get("task_id")}', 'job_id': job.job_id}

@router.post("/task/remove")
async def task_remove(task:TaskRemove,api_key:str = Security(get_api_key)) -> dict[str, str]:
    task = jsonable_encoder(task)
    print(task)
    db.remove_task(task)
    return {
        "info": "start page",
    }

@router.post("/task/pause")
async def task_pause(task:TaskPause,api_key:str = Security(get_api_key)) -> dict[str, str]:
    return {
        "info": "start page",
    }

@router.post("/task/status")
async def task_status(task:TaskStatus,api_key:str = Security(get_api_key)):
    job:Job = await redis_pool.get_task(task.opt_id)
    return {
        "info": job
    }

