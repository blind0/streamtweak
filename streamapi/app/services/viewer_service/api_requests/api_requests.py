import aiohttp
import re
from fake_useragent import UserAgent

class ApiRequest:
    def __init__(self,):
        pass

    @classmethod
    async def get_streamer_url(cls, username:str) -> str:
        async with aiohttp.ClientSession() as session:
            response = await session.get(f'https://www.twitch.tv/{username}', headers={"User-Agent": UserAgent().chrome})
            print(response.status)
            data = await response.text()
            settings_url = re.search(
                r"(https://static.twitchcdn.net/config/settings.*?js)",data).group(1)
            response = await session.get(settings_url, headers={"User-Agent": UserAgent().chrome})
            data = await response.text()
            spade_url = re.search(r'(?<=spade_url\":\").*?ts', data).group(0)
            return spade_url.strip()

    @classmethod
    async def get_channel_id(cls, username:str) -> str:
        async with aiohttp.ClientSession() as session:
            query = {
                "operationName": "ReportMenuItem",
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "8f3628981255345ca5e5453dfd844efffb01d6413a9931498836e6268692a30c",
                    }},
                "variables": {
                    "channelLogin": username}}
            print(username)
            data = await session.post("https://gql.twitch.tv/gql", headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko", "User-Agent": UserAgent().chrome}, json=query)
            json = await data.json()
            print(f'123:{json}')
            return json["data"]["user"]["id"]
    
    @classmethod
    async def get_broadcast_id(cls, channel_id:str):
        async with aiohttp.ClientSession() as session:
            query = {
                "operationName": "WithIsStreamLiveQuery",
                "variables": {
                    "id": channel_id},
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "04e46329a6786ff3a81c01c50bfa5d725902507a0deb83b0edbf7abe7a3716ea"}}}
            data = await session.post("https://gql.twitch.tv/gql", headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko", "User-Agent": UserAgent().chrome}, json=query)
            json = await data.json()
            stream = json["data"]["user"]["stream"]
            if stream is not None:
                return stream["id"]
            else:
                raise AttributeError
            
    @classmethod
    async def get_my_ip(cls, ):
        async with aiohttp.ClientSession() as session:
            resp = await session.get("https://api.ipify.org?format=json")
            response_data = await resp.json()
            return response_data['ip']