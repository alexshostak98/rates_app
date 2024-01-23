import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from json import JSONDecodeError, loads

import requests

from rates_app.utils import get_unix_timestamp
from rates_app.websocket.websocket_types import Rate


class AbstractRatesClient(ABC):

    @abstractmethod
    def get_rates(self, assets: dict[str, int]) -> list[Rate] | None:
        raise NotImplementedError


class EmcontRatesClient(AbstractRatesClient):
    url = 'https://rates.emcont.com/'

    def _call_api(self) -> dict | None:
        session = requests.Session()
        response = session.get(self.url)
        processed_response = re.findall(r'null\(([\w\W]+?})\);', response.text)
        if processed_response:
            try:
                return loads(processed_response[0]).get('Rates')
            except JSONDecodeError:
                logging.warning(f'Bad json response {processed_response}')
                return None

    def get_rates(self, assets: dict[str, int]) -> list[Rate] | None:
        raw_rates = self._call_api()
        if raw_rates is None:
            return raw_rates
        validated_rates = []
        timestamp = get_unix_timestamp(datetime.utcnow())
        for rate in raw_rates:
            asset_name = rate.get('Symbol')
            if asset_name in assets:
                value = (rate.get('Bid') + rate.get('Ask')) / 2
                validated_rates.append(
                    Rate(
                        asset=asset_name,
                        value=value,
                        timestamp=timestamp,
                        asset_id=assets.get(asset_name)
                    )
                )
        return validated_rates
