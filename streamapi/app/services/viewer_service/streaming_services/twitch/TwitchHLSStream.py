from aiohttp import ClientSession


class TwitchHLSStream:

    def __init__(self):
        pass
    
    @staticmethod
    async def _fetch_playlist(session:ClientSession,url:str,):
        async with session.get(url) as response:
            return await response.text()
    
    @staticmethod
    async def _parse_playlist(playlist:str):
        lines = playlist.split('\n')
        audio_only_url = None
        for line in lines:
            if 'VIDEO="audio_only"' in line:
                # The next line after this tag should be the URL
                index = lines.index(line)
                audio_only_url = lines[index + 1]
                break
        return audio_only_url

    @classmethod
    async def parse(cls, session:ClientSession, url:str):
        playlist = await cls._fetch_playlist(session, url)
        audio_only_url = await cls._parse_playlist(playlist)
        if not audio_only_url:
            return False
        
        return audio_only_url