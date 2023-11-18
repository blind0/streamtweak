from random import random
from aiohttp import ClientSession
from urllib.parse import urlencode    

class UsherService:
    def __init__(self, session: ClientSession):
        self.session: ClientSession = session

    async def _create_url(self, endpoint, **extra_params):
        base_url = f"https://usher.ttvnw.net{endpoint}"
        params = {
            "player": "twitchweb",
            "p": int(random() * 999999),
            "type": "any",
            "allow_source": "true",
            "allow_audio_only": "true",
            "allow_spectre": "false",
        }
        params.update(extra_params)
        url = f"{base_url}?{urlencode(params)}"
        return url

    async def channel(self, channel, **extra_params):
        url = await self._create_url(f"/api/channel/hls/{channel}.m3u8", **extra_params)
        return url

    async def video(self, video_id, **extra_params):
        url = await self._create_url(f"/vod/{video_id}", **extra_params)
        return url