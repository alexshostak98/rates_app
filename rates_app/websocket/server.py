from collections import defaultdict
from pydantic import ValidationError

import websockets
from websockets import WebSocketServerProtocol

from rates_app.clients.rates_clients import (
    AbstractRatesClient,
    EmcontRatesClient,
)
from rates_app import constants
from rates_app.database.services import DBService
from rates_app.websocket import websocket_types as types


class WebsocketManager:

    def __init__(self):
        self.subscriptions_count = defaultdict(list)
        self.clients: dict[int, set[WebSocketServerProtocol]] = defaultdict(set)
        self.rates_client: AbstractRatesClient = EmcontRatesClient()
        self.database_service = DBService()
        self.start_action_is_done = False

    async def subscribe(self, websocket: WebSocketServerProtocol, asset_id: int) -> None:
        self.clients[asset_id].add(websocket)

    async def unsubscribe(self, websocket: WebSocketServerProtocol, asset_id: int) -> None:
        self.clients[asset_id].remove(websocket)

    async def assets_history(self, websocket: WebSocketServerProtocol, asset_id: int) -> None:
        asset_history = await self.database_service.get_rates_history_by_asset_id_for_time_range(
            asset_id,
            constants.ASSET_HISTORY_TIME_RANGE,
        )
        server_event = types.WebSocketServerResponse(
            action=types.ServerAction.history,
            message=types.RatesMessage(points=asset_history)
        ).model_dump_json(by_alias=True)
        await websocket.send(server_event)

    @staticmethod
    async def send_error_message(websocket: WebSocketServerProtocol, message: str) -> None:
        server_event = types.WebSocketServerResponse(
            action=types.ServerAction.error,
            message=message
        ).model_dump_json()
        await websocket.send(server_event)

    async def check_errors(self, websocket: WebSocketServerProtocol, asset_id: int) -> None | str:
        message = None
        if self.start_action_is_done:
            assets = await self.database_service.get_assets()
            asset_ids = set(asset.id for asset in assets)
            if asset_id not in asset_ids:
                message = constants.ErrorMessages.wrong_asset_id.format(asset_id=asset_id)
        else:
            message = constants.ErrorMessages.wrong_start_action
        if message:
            await self.send_error_message(websocket, message)
        return message

    async def handle_subscribe_action(
        self,
        websocket: WebSocketServerProtocol,
        client_event: types.WebSocketClientRequest,
    ) -> None:
        asset_id = client_event.message.asset_id
        error_message = await self.check_errors(websocket, asset_id)
        if error_message is not None:
            return
        subscriptions_for_current_client = self.subscriptions_count[websocket]
        if len(subscriptions_for_current_client) >= constants.MAX_SUBSCRIPTIONS_COUNT_PER_CLIENT:
            await self.unsubscribe(websocket, subscriptions_for_current_client.pop(0))
        subscriptions_for_current_client.append(asset_id)
        await self.subscribe(websocket, asset_id)
        await self.assets_history(websocket, asset_id)

    async def handle_assets_action(
        self,
        websocket: WebSocketServerProtocol,
        client_event: types.WebSocketClientRequest,
    ) -> None:
        assets = await self.database_service.get_assets()
        server_event = types.WebSocketServerResponse(
            action=types.ServerAction.assets,
            message=types.AssetsMessage(assets=assets),
        )
        self.start_action_is_done = True
        await websocket.send(server_event.model_dump_json())

    async def handle_new_rates_action(
        self,
        websocket: WebSocketServerProtocol,
        client_event: types.WebSocketClientRequest,
    ):
        rates = client_event.message.points
        await self.database_service.create_rates_point(rates)
        for rate in rates:
            asset_id = rate.asset_id
            if asset_id in self.clients:
                server_event = types.WebSocketServerResponse(
                    action=types.ServerAction.point,
                    message=rate
                ).model_dump_json(by_alias=True)
                websockets.broadcast(self.clients[asset_id], server_event)

    @staticmethod
    def _get_help_event(action_type):
        server_event = types.WebSocketClientRequest(
            action=getattr(types.ClientAction, action_type),
            message=getattr(types.ExampleClientRequestMapper, action_type),
        )
        return types.HelpItem(
            priority=getattr(types.ClientActionPriorities, action_type),
            action=server_event,
            help_message=getattr(constants.HelpMessage, action_type),
        )

    async def handle_help_action(
        self,
        websocket: WebSocketServerProtocol,
        client_event: types.WebSocketClientRequest | None,

    ):
        help_items = [self._get_help_event(action_type) for action_type in types.ClientAction]
        help_server_event = types.WebSocketServerResponse(
            action=types.ServerAction.help,
            message=types.HelpMessage(actions=help_items)
        ).model_dump_json(by_alias=True)
        await websocket.send(help_server_event)

    async def produce_help_message(self, websocket):
        await self.handle_help_action(websocket, client_event=None)

    async def handler(self, websocket: WebSocketServerProtocol) -> None:
        await self.produce_help_message(websocket)
        async for websocket_message in websocket:
            try:
                client_event = types.WebSocketClientRequest.model_validate_json(websocket_message)
                action = client_event.action
            except ValidationError:
                message = constants.ErrorMessages.validation_error
                await self.send_error_message(websocket, message=message)
                # await self.produce_help_message(websocket)
                continue
            try:
                handle_func = getattr(self, f'handle_{action}_action')
                await handle_func(websocket, client_event)
            except AttributeError as exc:
                message = constants.ErrorMessages.unsupported_action.format(action=exc)
                await self.send_error_message(websocket, message=message)
                # await self.produce_help_message(websocket=websocket)
                continue
