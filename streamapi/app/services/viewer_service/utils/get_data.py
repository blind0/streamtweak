import asyncio
import aiohttp
from aiohttp import ClientSession
from fake_useragent import UserAgent

from app.db.database import DB

db = DB()

# async def get_proxies(proxy_filepath:str) -> list[str]:
#     async with aiofiles.open(proxy_filepath, mode='r') as proxy_file:
#         return await proxy_file.readlines()

# async def get_oauth(oauth_filepath:str) -> list[str]:
#     async with aiofiles.open(oauth_filepath, mode='r') as oauth_file:
#         data:str = await oauth_file.read()
#         oauth_list:list[str] = [oauth for oauth in data.splitlines()]
#         print(len(oauth_list))
#         return oauth_list

# def sync_oauth(oauth_filepath:str) -> list[str]:
#     with open(oauth_filepath,mode='r') as oauth_file:
#         data:str = oauth_file.read()
#         oauth_list:list[str] = [oauth for oauth in data.splitlines()]
#         print(len(oauth_list))
#         return oauth_list
    
# async def get_oauth_with_login(oauth_login_filepath:str) -> dict[str,str]:
#     async with aiofiles.open(oauth_login_filepath,mode='r') as oauth_login_file:
#         data:str = await oauth_login_file.read()
#         oauth_login_dict:dict[str,str] = {line for line in data.splitlines()}


async def check_proxy(session:ClientSession,proxy:str,ua:str):
    try:
        response = await session.get('https://www.twitch.tv/',headers={"User-Agent":ua},proxy=proxy, timeout=5)
    except asyncio.TimeoutError:
        return {proxy:0}
    except aiohttp.ClientProxyConnectionError:
        return {proxy:0}
    except aiohttp.ClientHttpProxyError:
        return {proxy:0}
    return {proxy:response.status}

async def check_token(session: aiohttp.ClientSession, token: str, ua: str):
    query = {
        "operationName": "PlaybackAccessToken",
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712"
            }
        },
        'variables': {
            "isLive": True,
            "login": "pewdiepie",
            "isVod": False,
            "vodID": "",
            "playerType": "site"
        }
    }
    resp = await session.post(url="https://gql.twitch.tv/gql", json=query, headers={"User-Agent": ua, "Authorization": f"OAuth {token}"})
    return {token: resp.status}


async def get_proxies(number):
    tasks:list = []
    result:list = []
    records:list = db.get_proxies(number)
    async with aiohttp.ClientSession() as session:
        tasks.extend(
            check_proxy(session=session, proxy=proxy, ua=UserAgent().chrome)
            for proxy in records
        )
        results:list = await asyncio.gather(*tasks)
        print(results)

    failed_count = 0

    for i in results:
        proxy:str = next(iter(i.keys()))
        if next(iter(i.values())) == 200:
            db.using_proxy(proxy)
            result.append(proxy)
        else:
            db.deactivate_proxy(proxy)
            failed_count+=1

    async with aiohttp.ClientSession() as session:
        while failed_count>0:
            new_proxy = db.get_proxy()
            check_res = await check_proxy(session,new_proxy,ua=UserAgent().chrome)
            if check_res[new_proxy] == 200:
                result.append(new_proxy)
                db.using_proxy(new_proxy)
                failed_count-=1
            else:
                db.deactivate_proxy(new_proxy)
    return result

async def get_oauth(number):
    tasks:list = []
    result:list = []
    records:list = db.get_twitch_tokens(number)

    async with aiohttp.ClientSession() as session:
        tasks.extend(
            check_token(session=session, token=token, ua=UserAgent().chrome)
            for token in records
        )
        results:list = await asyncio.gather(*tasks)

    failed_count:int = 0

    for i in results:
        token, status = next(iter(i.items()))
        if status == 200:
            db.using_token(token)  # Mark the token as being used
            result.append(token)
        else:
            db.deactivate_token(token)  # Deactivate the token
            failed_count += 1

    async with aiohttp.ClientSession() as session:
            while failed_count>0:
                new_token = db.get_twitch_token()
                check_res = await check_token(session,new_token,ua=UserAgent().chrome)
                if check_res[new_token] == 200:
                    db.using_token(new_token)
                    result.append(new_token)
                    failed_count-=1
                else:
                    db.deactivate_token(new_token)
    return result