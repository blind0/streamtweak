from app.services.viewer_service.core.viewer import AbstractStreamingService  # adjust import according to your project structure

from fake_useragent import UserAgent

from random import random
import re
import streamlink

class TwitchViewer(AbstractStreamingService):
    CLIENT_ID = 'ewvlchtxgqq88ru9gmfp1gmyt6h2b93'
    
    def __init__(self, id, absip, username, proxy, spade_url, channel_id, broadcast_id, oauth=None):
        super().__init__(id=id,absip=absip, proxy=proxy)
        self.username = username
        self.spade_url = spade_url
        self.channel_id = channel_id
        self.broadcast_id = broadcast_id
        self.oauth_token = oauth
        self.user_id = None
        self.device_id = None
        self.sig = None
        self.token = None
        self._request_link = None
        self.ua = UserAgent(min_percentage=1.3)
        print(self.session)
    
    @classmethod
    async def create(cls, id, absip, username: str, proxy: str, spade_url: str, channel_id: str, broadcast_id: str, oauth: str):
        return TwitchViewer(id=id, username=username, proxy=proxy, spade_url=spade_url, channel_id=channel_id, broadcast_id=broadcast_id, oauth=oauth, absip=absip)

    async def set_cookies(self):
        url = f'https://www.twitch.tv/{self.username}'
        await self.session.get(url, proxy=self.proxy)
        cookies = self.session.cookie_jar.filter_cookies("https://www.twitch.tv")
        self.device_id = cookies["unique_id"].value
    
    async def update_headers(self, headers=None):
        headers = headers or {
            'Client-Id': self.CLIENT_ID,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent': self.ua.getChrome,
            'Device-Id': self.device_id,
            "Authorization": f"OAuth {self.oauth_token}",
        }
        self.session.headers.update(headers)
    
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
        response_data = await self.post('https://gql.twitch.tv/gql', query)
        playback_token = response_data['data']["streamPlaybackAccessToken"]
        self.sig = playback_token["signature"]
        self.token = playback_token["value"]
        self.user_id = re.search(r'(?<=user_id\":)\d*', playback_token['value']).group(0)
    
    async def fetch_stream_data(self):
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
                data = await response.content.read()
                chunk = data.decode()
                start_index = chunk.rfind('VIDEO="audio_only"') + 19
                self._request_link = chunk[start_index:]
            else:
                print(f'error: {response.status}')

    async def viewer_request(self):
        return await self.session.head(url=self._request_link, proxy=self.proxy)

    
    async def init(self):
        await self.get_integrity_token()
        try:
            
            await self.set_cookies()
            await self.update_headers({
            "referer": "https://player.twitch.tv",
            "origin": "https://player.twitch.tv",
            })
            await self.get_stream_token()
        except Exception as e:
            print(f"Initialization failed: {e}")

    async def run(self):
        resp = await self.check_proxy()
        if not resp:
            return
        await self.fetch_stream_data()
        for _ in range(9):
            feed = await self.viewer_request()
        return feed
    
    async def check_proxy(self):
        async with self.session.get("https://api.ipify.org?format=json", proxy=self.proxy) as resp:
            json_data = await resp.json()
            return json_data['ip'] != self.absip
