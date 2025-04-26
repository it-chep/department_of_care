import pyrogram
from config.config import app_config

CLIENT_NAME = "readydog"


class TelegramClient(object):
    client: pyrogram.Client

    def __init__(self):
        self.client = pyrogram.Client(
            name=CLIENT_NAME,
            api_id=app_config.telegram.app_id,
            api_hash=app_config.telegram.app_hash,
        )
        self._is_connected = False

    async def start(self):
        if not self._is_connected:
            await self.client.start()
            self._is_connected = True

    
