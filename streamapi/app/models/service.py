from typing import List
from pydantic import BaseModel, FutureDatetime, Field
import uuid


class ProxyLoad(BaseModel):
    proxies: List[str] = Field(..., examples=[['proxy1','proxy2','...']])

class TokensLoad(BaseModel):
    tokens: List[str] = Field(..., examples=[['token1','token2','...']])