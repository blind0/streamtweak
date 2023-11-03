from app.services.viewer_service.core.viewer import Viewer
from app.services.viewer_service.utils.get_data import get_proxies, get_oauth
from app.services.viewer_service.api_requests.api_requests import ApiRequest

import asyncio
import random
from aiohttp import ClientSession
from uuid import uuid4, UUID
from typing import Dict


class ViewerPool:
    CLIENT_ID = 'kimne78kx3ncx6brgo4mv6wki5h1ko'

    def __init__(self, username, number):
        self.username:str = username
        self.number:int = number
        self.session = ClientSession()
        self.instances: Dict[UUID,Viewer] = {} 
        self.spade_url:str = ''
        self.channel_id:str = ''
        self.broadcast_id:str = ''
        self.myip = None

    
    async def _initialize_viewer(self, proxy, oauth_token):
        uid = uuid4()
        viewer = await Viewer.create(
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
        proxy_lines = await get_proxies(self.number)
        oauth_lines = await get_oauth(self.number)
        tasks = [
            self._initialize_viewer(proxy.strip(), oauth_token)
            for proxy, oauth_token in zip(proxy_lines, oauth_lines)
        ]
        await asyncio.gather(*tasks)

    # async def viewer_init(self, instance: Viewer):
    #     await instance.init()
    #     print(f'{instance.proxy} instance initialized successfully')

    async def viewer_request(self, instance: Viewer):
        await instance.run()

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
                tasks = [self.viewer_request(instance) for instance in self.instances.values()]
                await asyncio.gather(*tasks)
                print('loop was iterated')
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            await self.close_sessions()
