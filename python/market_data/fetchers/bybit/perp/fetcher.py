"""
Data fetcher that connects to the OKX exchange and fetches spot market data
"""

from typing import List
import json

from python.types.enums.asset_type import AssetType
from python.types.enums.exchange_name import ExchangeName
from python.market_data.fetchers.fetcher import MarketDataFetcher
from python.types.tick_record import TickRecord
from python.market_data.fetchers.bybit.data_transformer import BybitOrderBookDataTransformer


class BybitPerpMarketDataFetcher(MarketDataFetcher):
    """
    Data fetcher that connects to the OKX exchange and fetches spot market data
    """

    def websocket_url(self) -> str:
        return "wss://stream.bybit.com/v5/public/linear"

    def subscription_arguments_str(self) -> str:
        return json.dumps({
            "op": "subscribe",
            "args": [
                f"orderbook.50.{self.instrument}"
            ],
        })

    def transform_json_to_tick_record(
        self,
        message: str,
        receive_timestamp: int
    ) -> List[TickRecord]:
        return BybitOrderBookDataTransformer.transform_json_message(
            message,
            receive_timestamp
        )

    @staticmethod
    def supported_instruments() -> List[str]:
        return ["BTCUSDT", "ETHUSDT"]

    @staticmethod
    def supported_instruments_for_test() -> List[str]:
        return ["BTCUSDT", "ETHUSDT"]

    @staticmethod
    def supported_asset_type() -> AssetType:
        return "PERP"

    @staticmethod
    def exchange_name() -> ExchangeName:
        return ExchangeName.BYBIT
