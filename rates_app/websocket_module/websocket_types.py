from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ServerAction(StrEnum):
    assets = 'assets'
    history = 'asset_history'
    point = 'point'
    error = 'error'


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


class WebSocketServerResponse(BaseModel):
    action: str
    message: Rate | AssetsMessage | RatesMessage | str


# WebSocketClient types

class ClientAction(StrEnum):
    assets = 'assets'
    subscribe = 'subscribe'
    new_rates = 'new_rates'


class SubscribeMessage(BaseModel):
    asset_id: int = Field(validation_alias='assetId')


class WebSocketClientRequest(BaseModel):
    action: str
    message: SubscribeMessage | RatesMessage | dict
