from app.services.viewer_service.streaming_services.twitch.TwitchApi import TwitchAPI
from app.services.viewer_service.streaming_services.twitch.UsherService import UsherService
from app.services.viewer_service.streaming_services.twitch.TwitchHLSStream import TwitchHLSStream
from app.services.viewer_service.streaming_services.twitch.TwitchClientIntegrity import TwitchClientIntegrity

import aiohttp
from aiohttp import ClientSession



class Twitch:
    _CACHE_KEY_CLIENT_INTEGRITY = "client-integrity"

    def __init__(self, channel_id, session, device_id):
        self.channel: str = channel_id
        self.session: ClientSession = session  # This should be an instance of aiohttp.ClientSession passed from outside
        self.device_id: str = device_id
        # Initialize other attributes
        self.api:TwitchAPI = TwitchAPI(self.session)
        self.usher:UsherService = UsherService(self.session)

    async def _client_integrity_token(self, channel: str):
        device_id = self.device_id
        token, expiration = await TwitchClientIntegrity.acquire(
            self.session,
            channel,
            self.api.headers,
            device_id,
        )
        if not token:
            return None

        self.cache.set(self._CACHE_KEY_CLIENT_INTEGRITY, [device_id, token], expires_at=fromtimestamp(expiration))

        return device_id, token
    

    async def _access_token(self, is_live, channel):
        # try without a client-integrity token first (the web player did the same on 2023-05-31)
        response, *data = self.api.access_token(is_live, channel)

        # try again with a client-integrity token if the API response was erroneous
        if response != "token":
            client_integrity = self._client_integrity_token(channel) if is_live else None
            response, *data = self.api.access_token(is_live, channel, client_integrity)

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
            if self._check_for_rerun():
                return None
            
            # Get the access token, signature, and any other necessary parameters
            sig, token = await self.api.access_token(True, self.channel)
            # Construct the HLS URL
            url = await self.usher.channel(self.channel, sig=sig, token=token, fast_bread=True)

            # Process the HLS playlist text to extract the stream information
            # Assuming there's a method to parse the playlist and return stream objects
            streams = await self._get_hls_streams(url, force_restart=True)

            return streams

    async def _get_hls_streams(self, url):

        streams = TwitchHLSStream.parse(self.session, url)

        return streams

    async def _get_streams(self):
        return await self._get_hls_streams_live()
