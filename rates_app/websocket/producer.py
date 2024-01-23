import websockets

from rates_app import settings


async def websocket_producer(message: str):
    async with websockets.connect(uri=settings.SERVER_URI) as websocket:
        await websocket.send(message)
