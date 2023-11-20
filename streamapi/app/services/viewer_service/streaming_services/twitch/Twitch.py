from app.services.viewer_service.streaming_services.twitch.TwitchApi import TwitchAPI
from app.services.viewer_service.streaming_services.twitch.UsherService import UsherService
from app.services.viewer_service.streaming_services.twitch.TwitchHLSStream import TwitchHLSStream
from app.services.viewer_service.streaming_services.twitch.TwitchClientIntegrity import TwitchClientIntegrity
from app.core.cache import Cache

import aiohttp
from aiohttp import ClientSession

cache=Cache()

class Twitch:
    _CACHE_KEY_CLIENT_INTEGRITY = "client-integrity"

    def __init__(self, channel_id, session, device_id, oauth,proxy):
        self.channel: str = channel_id
        self.session: ClientSession = session  # This should be an instance of aiohttp.ClientSession passed from outside
        self.device_id: str = device_id
        self.oauth: str = oauth
        self.proxy = proxy
        # Initialize other attributes
        self.api:TwitchAPI = TwitchAPI(self.session,self.proxy)
        self.usher:UsherService = UsherService(self.session)

    async def _client_integrity_token(self, channel: str):
        device_id = self.device_id
        client_integrity = await cache.get_timestamp_cache(self._CACHE_KEY_CLIENT_INTEGRITY)
        
        if client_integrity:
            return device_id, client_integrity
        else:
            client_integrity = await TwitchClientIntegrity.acquire(
                self.session,
                channel,
                self.api.headers,
                device_id,
                self.oauth,
                self.proxy
            )
            if not client_integrity:
                return None
        token, expiration = client_integrity
        await cache.set_timestamp_cache(self._CACHE_KEY_CLIENT_INTEGRITY,token,expiration)
        return device_id, token
    

    async def _access_token(self, is_live, channel):
        # try without a client-integrity token first (the web player did the same on 2023-05-31)
        response, *data = await self.api.access_token(is_live, channel,oauth = self.oauth)

        # try again with a client-integrity token if the API response was erroneous
        if response != "token":
            client_integrity = await self._client_integrity_token(channel) if is_live else None
            response, *data = await self.api.access_token(is_live, channel, client_integrity, oauth = self.oauth)

            # unknown API response error: abort
            if response != "token":
                error, message = data
                raise Exception(f"{error or 'Error'}: {message or 'Unknown error'}")

        # access token response was empty: stream is offline or channel doesn't exist
        if response == "token" and data is None:
            raise Exception('NoStreamsError')
        
        sig, token = data

        return sig, token

    async def _check_for_rerun(self):
        try:
            stream = await self.api.stream_metadata(self.channel)
            if stream["type"] != "live":
                print("Reruns were disabled by command line option")
                return True
        except:
            pass

        return False

    async def _get_hls_streams_live(self):
            if await self._check_for_rerun():
                return None
            self.session.headers.update({
            "referer": "https://player.twitch.tv",
            "origin": "https://player.twitch.tv",
        })
            sig, token = await self._access_token(True, self.channel)
            url = await self.usher.channel(self.channel, sig=sig, token=token, fast_bread=True)

            streams = await self._get_hls_streams(url, force_restart=True,proxy=self.proxy)

            return streams

    async def _get_hls_streams(self, url, proxy):

        streams = await TwitchHLSStream.parse(self.session, url, proxy=proxy)

        return streams

    async def get_streams(self):
        return await self._get_hls_streams_live()
