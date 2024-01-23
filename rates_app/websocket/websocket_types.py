from enum import StrEnum, IntEnum

from pydantic import BaseModel, ConfigDict, Field


class ServerAction(StrEnum):
    assets = 'assets'
    history = 'asset_history'
    point = 'point'
    error = 'error'
    help = 'help'


class ClientAction(StrEnum):
    help = 'help'
    assets = 'assets'
    subscribe = 'subscribe'


class InnerClientAction(StrEnum):
    new_rates = 'new_rates'
    help = 'help'


class ClientActionPriorities(IntEnum):
    help = 0
    assets = 1
    subscribe = 2


# WebSocketServer types
class Asset(BaseModel):
    model_config = ConfigDict(from_attributes=True, revalidate_instances='always')

    id: int
    name: str


class Rate(BaseModel):
    model_config = ConfigDict(from_attributes=True, revalidate_instances='always')

    asset: str = Field(serialization_alias='assetName')
    timestamp: int = Field(serialization_alias='time')
    asset_id: int = Field(serialization_alias='assetId')
    value: float


class AssetsMessage(BaseModel):
    assets: list[Asset]


class RatesMessage(BaseModel):
    points: list[Rate]


# WebSocketClient types
class SubscribeMessage(BaseModel):
    asset_id: int = Field(alias='assetId')


class WebSocketClientRequest(BaseModel):
    action: str
    message: SubscribeMessage | RatesMessage | dict


class ExampleClientRequestMapper:
    default_value = {}
    assets = default_value
    help = default_value
    subscribe = SubscribeMessage(assetId=1)


# WebSocketServer types
class HelpItem(BaseModel):
    priority: int
    action: WebSocketClientRequest
    help_message: str


class HelpMessage(BaseModel):
    actions: list[HelpItem]


class WebSocketServerResponse(BaseModel):
    action: str
    message: Rate | AssetsMessage | RatesMessage | HelpMessage | str
