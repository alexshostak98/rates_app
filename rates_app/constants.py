from datetime import timedelta
from enum import StrEnum

MAX_SUBSCRIPTIONS_COUNT_PER_CLIENT = 1

ASSET_HISTORY_TIME_RANGE = timedelta(minutes=30)


class RequiredAssets(StrEnum):
    eur_to_usd = 'EURUSD'
    usd_to_jpy = 'USDJPY'
    gpb_to_usd = 'GBPUSD'
    aud_to_usd = 'AUDUSD'
    usd_to_cad = 'USDCAD'


class ErrorMessages(StrEnum):
    unsupported_action = 'Unsupported action: {action}. Please select from available actions.'
    wrong_start_action = 'Please start with "assets" action.'
    wrong_asset_id = 'Wrong asset_id: {asset_id}. This asset is not supported.'
    validation_error = 'Can not process input message. Please select from available actions.'


class HelpMessage(StrEnum):
    assets = 'Get list of available assets.'
    subscribe = (
        'Subscribe to rates one of the available assets by its id. '
        'Only one asset subscription is available at a time. '
        'To subscribe to new asset, send the message again, specifying the new id.'
    )
    help = 'Get information about available actions.'
