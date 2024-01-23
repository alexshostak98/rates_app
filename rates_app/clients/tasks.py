import asyncio

from celery import shared_task

from rates_app.clients.rates_clients import EmcontRatesClient
from rates_app.database.services import DBService
from rates_app.websocket import websocket_types as types
from rates_app.websocket.producer import websocket_producer


@shared_task()
def get_rates_by_client():
    db_service = DBService()
    rates_client = EmcontRatesClient()
    supported_assets = asyncio.run(db_service.get_assets())
    transformed_assets = {asset.name: asset.id for asset in supported_assets}
    rates = rates_client.get_rates(transformed_assets)
    if rates is not None:
        message = types.WebSocketClientRequest(
            action=types.InnerClientAction.new_rates,
            message=types.RatesMessage(points=rates)
        ).model_dump_json()
        asyncio.run(websocket_producer(message))
