from app.services.viewer_service.core.pool import ViewerPool
from app.services.viewer_service.streaming_services.twitch.TwitchViewer import TwitchViewer

class Application:
    def __init__(self, username, number):   
        self.username = username
        self.number = number
    async def run(self):
        p = ViewerPool(TwitchViewer,self.username,self.number)
        await p.start()