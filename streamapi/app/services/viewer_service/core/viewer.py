from app.services.viewer_service.utils.minute_watched import get_minute_watched_payload

from aiohttp import ClientSession
from fake_useragent import UserAgent
from random import random
from uuid import UUID

import abc
import asyncio
import re
import logging
import traceback

class TwitchAPI:
    BASE_URL = 'https://www.twitch.tv'
    GQL_URL = 'https://gql.twitch.tv/gql'
    USHER_URL = "https://usher.ttvnw.net/api/channel/hls/{username}.m3u8"

    def __init__(self, session, username, proxy):
        self.session = session
        self.username = username
        self.proxy = proxy
        self.headers = {}

    async def set_cookies(self):
        url = f'{self.BASE_URL}/{self.username}'
        await self.session.get(url, headers=self.headers, proxy=self.proxy)

    async def update_headers(self, headers):
        self.headers.update(headers)

    async def post(self, url, json_data):
        async with self.session.post(url, json=json_data, headers=self.headers, proxy=self.proxy) as response:
            return await response.json()

    async def get(self, url, params=None):
        async with self.session.get(url, params=params, headers=self.headers, proxy=self.proxy) as response:
            return await response.json()

class Viewer:
    def __init__(
        self,
        id:UUID,
        username: str,
        proxy: str,
        absip: str,
        spade_url1: str,
        channel_id: str,
        broadcast_id: str,
        oauth: str = None,
    ):
        self.id = id 
        self.username = username.lower()
        self.client_id = 'ewvlchtxgqq88ru9gmfp1gmyt6h2b93'
        self.spade_url = spade_url1
        self.oauth_token = oauth
        self.channel_id = channel_id
        self.broadcast_id = broadcast_id
        self.user_id: str = None
        self.device_id: str = None
        self.ua = UserAgent().chrome
        self.proxy = proxy
        self.absip = absip
        self.session = ClientSession()
        self._cookies = {}
        self.sig:str = None
        self.token:str = None 
        self._request_link:str = None

    @classmethod
    async def create(cls,id:UUID, username: str, proxy: str, absip: str, spade_url: str, channel_id: str, broadcast_id: str, oauth: str = None, ):
        return Viewer(
            id=id,
            username=username,
            proxy=proxy,
            absip=absip,
            oauth=oauth,
            spade_url1=spade_url,
            channel_id=channel_id,
            broadcast_id=broadcast_id)

    async def close_conn(self):
        await self.session.close()

   # async def viewer_list_add(self):


    async def headers_init(self):
        headers = {
            'Client-Id': self.client_id,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent': self.ua,
            'Device-Id':self.device_id,
            "Authorization": f"OAuth {self.oauth_token}",
        }

        self.session.headers.update(headers)

    async def set_cookies(self):
        await self.session.get(f'https://www.twitch.tv/{self.username}', proxy=self.proxy)
        cookies = self.session.cookie_jar.filter_cookies("https://www.twitch.tv")
        self.device_id = cookies["unique_id"].value
        #print(f'{self.id} | {self.device_id}')

    async def minute_watched_request(self,):
        payload = await get_minute_watched_payload(
            channel_id=self.channel_id,
            broadcast_id=self.channel_id,
            device_id=self.device_id,
            user_id=self.user_id)
        resp = await self.session.post(url=self.spade_url,data=payload,)
        #print(resp.status)
    
    async def get_stream_token(self):
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
                "login": self.username,
                "isVod": False,
                "vodID": "",
                "playerType": "site"
            }
        }
        async with self.session.post(url='https://gql.twitch.tv/gql', json=query, proxy=self.proxy) as response:
            response_data = await response.json()
            playback_token = response_data['data']["streamPlaybackAccessToken"]
            self.sig = playback_token["signature"]
            self.token = playback_token["value"]
            self.user_id = re.search(r'(?<=user_id\":)\d*',playback_token['value']).group(0)


    async def check_proxy(self):
        async with self.session.get("https://api.ipify.org?format=json", proxy=self.proxy) as resp:
            json_data = await resp.json()
            return json_data['ip'] != self.absip

    async def usher_request(self):
        url = f"https://usher.ttvnw.net/api/channel/hls/{self.username}.m3u8"
        params = {
            "player": "twitchweb",
            "p": int(random() * 999999),
            "type": "any",
            "allow_source": "true",
            "allow_audio_only": "true",
            "allow_spectre": "false",
            "sig": self.sig,
            "token": self.token
        }

        async with self.session.get(url, params=params, proxy=self.proxy) as response:
            if response.status == 403:
                if (await response.json())[0]['error'] == 'expired token':
                    await self.get_stream_token()

            if response.status == 200:
                #print(f'{self.id} status | 200')
                data = await response.content.read()
                chunk = data.decode()
                start_index = chunk.rfind('VIDEO="audio_only"') + 19
                self._request_link = chunk[start_index:]
                print(f'{self.id}|{self._request_link}')
            else:
                print(f'error: {response.status}')


    async def viewer_request(self):
        return await self.session.head(url=self._request_link, proxy=self.proxy)

    async def init(self):
        try:
            await self.set_cookies()
            await self.headers_init()
            await self.get_stream_token()
        except:
            logging.error(traceback.format_exc())

    async def run(self):
        resp = await self.check_proxy()
        #print(f'ip: {resp}')
        if not resp:
            return

        #await self.minute_watched_request()
        await self.usher_request()
        for _ in range(9):
            feed = await self.viewer_request()
        return feed


async def main():
    a = await Viewer.create('senatorov1', 'http://wlrmslrtoer:k4j3kds853@45.61.116.58:6736', '95.78.147.40')
    await a.init()

    