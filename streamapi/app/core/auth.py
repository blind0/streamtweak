from app.core.config import MASTER_API_SECRET_KEY
from app.db.database import DB

from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


api_key_header = APIKeyHeader(name="access_token", auto_error=False)

db = DB()

async def get_master_api_key(api_key_header: str = Security(api_key_header)) -> str: 
    if api_key_header == MASTER_API_SECRET_KEY:
        return api_key_header   
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate API KEY"
        )

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    ans = db.check_api_key(api_key_header)
    if ans is not None:
        return api_key_header   
    else:
        raise HTTPException(    
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate API KEY"
        )
