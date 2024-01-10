import asyncio

import websockets

from rates_app import settings
from rates_app.websocket_module.server import WebsocketManager


async def main():
    manager = WebsocketManager()
    async with websockets.serve(
            manager.handler,
            settings.SERVER_HOST,
            settings.SERVER_PORT,
    ):
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
