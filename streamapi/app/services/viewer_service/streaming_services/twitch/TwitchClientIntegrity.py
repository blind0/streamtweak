from aiohttp import ClientSession
from typing import Mapping, Optional, Tuple
from json import dumps as json_dumps
from json import loads as json_loads
import base64

class TwitchClientIntegrity:
    @staticmethod
    async def _get_integrity_token(session,headers,device_id,oauth,proxy):
        headers = headers
        headers['Device-Id'] = device_id
        headers['Authorization'] = f"OAuth {oauth}"
        try:
            async with session.post("https://gql.twitch.tv/integrity", headers=headers,proxy=proxy) as response:
                if response.status != 200:
                    raise Exception("Failed to generate integrity")
                
                res_body = await response.json()
                if res_body.get('error'):
                    raise Exception(res_body.get('message'))
                
                return {
                    "error": False, 
                    "expired": res_body.get('expiration'),
                    "token": res_body.get('token'), 
                }
            
        except Exception as err:
            return {"error": True, "message": str(err)}
        
    @staticmethod
    async def decode_client_integrity_token(data: str):
        if not data.startswith("v4.public."):
            raise Exception("Invalid client-integrity token format")
        token = data[len("v4.public."):].replace("-", "+").replace("_", "/")
        token += "=" * ((4 - (len(token) % 4)) % 4)
        token = base64.b64decode(token.encode())[:-64].decode()
        return json_loads(token)
    
    @classmethod
    async def acquire(
        cls,
        session: ClientSession,
        channel: str,
        headers: Mapping[str, str],
        device_id: str,
        oauth:str,
        proxy,
    ):  
        client_integrity = await cls._get_integrity_token(session,headers,device_id,oauth,proxy)
        token, expiration = client_integrity.get('token'), client_integrity.get('expired')
        is_bad_bot = await cls.decode_client_integrity_token(token)
        is_bad_bot = is_bad_bot.get('is_bad_bot')
        print(f"ISBAD::::{is_bad_bot}")
        if is_bad_bot:
            return None

        return token, expiration / 1000