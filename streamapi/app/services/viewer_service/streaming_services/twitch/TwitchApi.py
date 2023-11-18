from aiohttp import ClientSession
from typing import Optional, Tuple
import asyncio
import aiohttp

class TwitchAPI:
    CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"

    def __init__(self, session: ClientSession):
        self.session: ClientSession = session
        self.headers = {
            "Client-ID": self.CLIENT_ID,
        }


    async def stream_metadata(self, channel):
        query = {
            "operationName": "StreamMetadata",
            "extensions": {
                "persistedQuery":{
                    "version": 1,
                    "sha256Hash":"1c719a40e481453e5c48d9bb585d971b8b372f8ebb105b17076722264dfa5b3e"
                }
                },
                "variables":{
                    "channelLogin":channel
                }
        }
        async with self.session.post(
            "https://gql.twitch.tv/gql",
            json=query,
            headers=self.headers
        ) as response:
            return response['data']['user']['stream']['type']

    async def access_token(self, is_live, channel, client_integrity: Optional[Tuple[str, str]] = None):
        query = {
                "operationName": "PlaybackAccessToken",
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712"
                    }
                },
                "variables": {
                    "isLive": is_live,
                    "login": channel if is_live else "",
                    "isVod": not is_live,
                    "vodID": "",
                    "playerType": "site"
                }
            }
        headers = self.headers.copy()
            # If there's an integrity token, it should be added to headers here

        async with self.session.post(
            "https://gql.twitch.tv/gql",
            json=query,
            headers=headers
        ) as response:
            response.raise_for_status()
            data = await response.json()

        # Here you would extract the 'sig', 'token', and 'restricted_bitrates' from the response
        # Since the structure of the response is not provided, this is a placeholder for the extraction logic
        if data.get('error'):
            return 'error', data['error'],data['message']
        
        response = 'token'
        sig = data['data']["streamPlaybackAccessToken"]["signature"]
        token = data['data']["streamPlaybackAccessToken"]['value']

        return response, sig, token


