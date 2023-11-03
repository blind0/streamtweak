from fastapi import APIRouter, Depends, Security, Body
from fastapi.encoders import jsonable_encoder
from arq.jobs import Job

from app.core.auth import get_master_api_key, get_api_key
from app.core.arq import RedisPool
from app.api.api import get_token
from app.db.database import DB
from app.models.service import ProxyLoad, TokensLoad


router = APIRouter()
db = DB()
redis_pool = RedisPool()

@router.get("/token/get")
async def token_get(api_key: str = Security(get_master_api_key)) -> dict[str,str]:
    token = await get_token()
    db.create_api_key(token)
    return {'token':token}

@router.put("/twitch_token/load")
async def load_twitch_tokens(api_key: str = Security(get_api_key), tokens_list:TokensLoad = Body(...)) -> dict[str,str]:
    json_body = jsonable_encoder(tokens_list)
    tokens_list = json_body['tokens']
    feed = db.load_tokens(tokens_list)
    return feed

@router.put("/proxy/load")
async def load_proxies(api_key: str = Security(get_api_key), proxy_list:ProxyLoad = Body(...)) -> dict[str,str]:
    json_body = jsonable_encoder(proxy_list)
    proxies_list = json_body['proxies']
    feed = db.load_proxies(proxies_list)
    return feed