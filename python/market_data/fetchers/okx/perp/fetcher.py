"""
Data fetcher that connects to the OKX exchange and fetches spot market data
"""

from typing import List
import json

from python.types.enums.asset_type import AssetType
from python.market_data.fetchers.fetcher import MarketDataFetcher
from python.market_data.fetchers.okx.data_transformer import OKXOrderBookDataTransformer
from python.types.tick_record import TickRecord
from python.types.enums.exchange_name import ExchangeName


class OKXPerpMarketDataFetcher(MarketDataFetcher):
    """
    Data fetcher that connects to the OKX exchange and fetches perp market data
    """

    def websocket_url(self) -> str:
        return "wss://ws.okx.com:8443/ws/v5/public"

    def subscription_arguments_str(self) -> str:
        return json.dumps({
            "op": "subscribe",
            "args": [{"channel": "books", "instId": self.instrument}],
        })

    def transform_json_to_tick_record(
            self,
            message: str,
            receive_timestamp: int
    ) -> List[TickRecord]:
        return OKXOrderBookDataTransformer.transform_json_message(
            message,
            receive_timestamp
        )

    @staticmethod
    def supported_instruments() -> List[str]:
        return ["BTC-USDT-SWAP"]

    @staticmethod
    def supported_instruments_for_test() -> List[str]:
        return ["BTC-USDT-SWAP"]

    @staticmethod
    def supported_asset_type() -> AssetType:
        return "PERP"

    @staticmethod
    def exchange_name() -> ExchangeName:
        return ExchangeName.OKX
