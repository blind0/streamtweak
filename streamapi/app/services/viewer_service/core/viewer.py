from abc import ABC, abstractmethod
from aiohttp import ClientSession

class AbstractStreamingService(ABC):
    def __init__(self, id, proxy, absip):
        self.id = id
        self.proxy = proxy
        self.absip = absip
        self.session = ClientSession()
    
    @abstractmethod
    async def create(self):
        ...

    @abstractmethod
    async def init(self):
        ...

    @abstractmethod
    async def set_cookies(self):
        ...

    @abstractmethod
    async def update_headers(self, headers):
        ...

    @abstractmethod
    async def get_stream_token(self):
        ...

    @abstractmethod
    async def fetch_stream_data(self):
        ...

    @abstractmethod
    async def init(self):
        ...

    @abstractmethod
    async def run(self):
        ...

    async def post(self, url, json_data):
        async with self.session.post(url, json=json_data, proxy=self.proxy) as response:
            return await response.json()
    
    async def get(self, url, params=None):
        async with self.session.get(url, params=params, proxy=self.proxy) as response:
            return await response.json()
    
    async def close_session(self):
        await self.session.close()
