from app.services.viewer_service.core.viewer import AbstractStreamingService
from app.services.viewer_service.streaming_services.twitch.TwitchViewer import TwitchViewer
from app.services.viewer_service.utils.get_data import get_proxies, get_oauth
from app.services.viewer_service.api_requests.api_requests import ApiRequest

import asyncio
from random import random
from aiohttp import ClientSession
from uuid import uuid4, UUID
from typing import Dict, Type, Union

class ViewerPool:
    def __init__(self, service_class: Type[AbstractStreamingService], username: str, number: int):
        self.service_class:Type[AbstractStreamingService] = service_class
        self.username = username
        self.number = number
        self.session = ClientSession()
        self.instances: Dict[uuid4, AbstractStreamingService] = {}
        self.spade_url = ''
        self.channel_id = ''
        self.broadcast_id = ''
        self.myip = None

    
    async def _initialize_viewer(self, proxy, oauth_token):
        uid = uuid4()
        viewer = await self.service_class.create(
            id=uid,
            username=self.username,
            proxy=proxy,
            absip=self.myip,
            spade_url=self.spade_url,
            channel_id=self.channel_id,
            broadcast_id=self.broadcast_id,
            oauth=oauth_token
        )
        await viewer.init()
        self.instances[uid] = viewer
        print(f'{viewer.proxy} instance initialized successfully')

    async def init_instances(self):
        if self.service_class is TwitchViewer:
            proxy_lines = await get_proxies(self.number)
            oauth_lines = await get_oauth(self.number)
            tasks = [
                self._initialize_viewer(proxy.strip(), oauth_token)
                for proxy, oauth_token in zip(proxy_lines, oauth_lines)
            ]
        else:
            raise ValueError("Invalid service type")
        await asyncio.gather(*tasks)

    async def close_sessions(self):
        tasks = [instance.close_conn() for instance in self.instances.values()]
        await asyncio.gather(*tasks)

    async def start(self):
        self.myip = await ApiRequest.get_my_ip()
        self.spade_url = await ApiRequest.get_streamer_url(self.username)
        self.channel_id = await ApiRequest.get_channel_id(self.username)
        self.broadcast_id = await ApiRequest.get_broadcast_id(self.channel_id)
        await self.init_instances()
        try:
            while True:
                tasks = [instance.run() for instance in self.instances.values()]
                await asyncio.gather(*tasks)
                print('loop was iterated')
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            await self.close_sessions()
