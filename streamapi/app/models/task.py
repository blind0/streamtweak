from typing import Union
from pydantic import BaseModel, FutureDatetime, Field
import uuid

class TaskCreate(BaseModel):
    task_id: str | None = Field(default_factory=uuid.uuid4,description='task id')
    type_task: str = Field(description='task type')
    channel_name: str = Field(description='twitch channel name')
    viewer_number: int | None = Field(description='number of viewer')
    interval: float | None = Field(description='interval of connection')
    exp_time: FutureDatetime | None = Field(description='time of work')
    active: bool = False
    
    model_config = {
        "json_schema_extra" : {
            "examples":[{
                "task_id":'7ae6bf4f-c206-42f5-84a7-8612a5eb111e',
                'type_task':'viewers',
                'channel_name':"twitcherBoy147",
                'viewer_number':500,
                'interval':1.5,
                'exp_time':1695994841,
            }]  
        }
    }

class TaskRemove(BaseModel):
    task_id: str = Field(...)

class TaskPause(BaseModel):
    task_id: str = Field(...)

class TaskStatus(BaseModel):
    task_id: str = Field(...)
    opt_id:str = Field(...)