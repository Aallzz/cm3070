"""
Logic for fetching in processing market data from the Hyperliquid exchange
"""

from typing import List
import json

from python.market_data.fetchers.hyperliquid.data_transformer import HyperliquidDataTransformer
from python.market_data.fetchers.fetcher import MarketDataFetcher
from python.types.enums.asset_type import AssetType
from python.types.enums.exchange_name import ExchangeName
from python.types.tick_record import TickRecord


class HyperliquidMarketDataFetcher(MarketDataFetcher):
    """
    Data fetcher that connectes for websockets to the Hyperliquid exchange
    and fetches market data 
    """

    def websocket_url(self) -> str:
        return "wss://api.hyperliquid.xyz/ws"

    def subscription_arguments_str(self) -> str:
        return json.dumps({
            "method": "subscribe",
            "subscription": {
                "type": "l2Book",
                "coin": self.instrument
            }
        })

    def transform_json_to_tick_record(
        self,
        message: str,
        receive_timestamp: int
    ) -> List[TickRecord]:
        return HyperliquidDataTransformer.transform_json_message(
            message,
            receive_timestamp
        )

    @staticmethod
    def supported_instruments() -> List[str]:
        return [
            "BTC", "ETH", "ATOM", "MATIC",
            "DYDX", "SOL", "AVAX", "BNB",
            "APE", "OP", "LTC", "ARB",
            "DOGE", "INJ", "SUI", "kPEPE",
            "CRV", "LDO", "LINK", "STX",
            "RNDR", "CFX", "FTM", "GMX",
            "SNX", "XRP", "BCH", "APT",
            "AAVE", "COMP", "WLD", "FXS",
            "HPOS", "RLB", "UNIBOT", "YGG",
            "TRX", "kSHIB", "UNI", "SEI",
            "RUNE", "OX", "FRIEND", "SHIA",
            "CYBER", "ZRO", "BLZ", "DOT",
            "BANANA", "TRB", "FTT", "LOOM",
            "OGN", "RDNT", "ARK", "BNT",
            "CANTO", "REQ", "BIGTIME", "KAS",
            "ORBS", "BLUR", "TIA", "BSV",
            "ADA", "TON", "MINA", "POLYX",
            "GAS", "PENDLE", "STG", "FET",
            "STRAX", "NEAR", "MEME", "ORDI",
            "BADGER", "NEO", "ZEN", "FIL",
            "PYTH", "SUSHI", "ILV", "IMX",
            "kBONK", "GMT", "SUPER", "USTC",
            "NFTI", "JUP", "kLUNC", "RSR",
            "GALA", "JTO", "NTRN", "ACE",
            "MAV", "WIF", "CAKE", "PEOPLE",
            "ENS", "ETC", "XAI", "MANTA",
            "UMA", "ONDO", "ALT", "ZETA",
            "DYM", "MAVIA", "W", "PANDORA",
            "STRK", "PIXEL", "AI", "TAO",
            "AR", "MYRO", "kFLOKI", "BOME",
            "ETHFI", "ENA", "MNT", "TNSR",
            "SAGA", "MERL", "HBAR", "POPCAT",
            "OMNI", "EIGEN", "REZ"
        ]

    @staticmethod
    def supported_instruments_for_test() -> List[str]:
        return ["BTC", "ETH"]

    @staticmethod
    def supported_asset_type() -> AssetType:
        return "PERP"

    @staticmethod
    def exchange_name() -> ExchangeName:
        return ExchangeName.HYPERLIQUID
