"""
List of all fetchers in use
"""

from python.market_data.fetchers.hyperliquid.perp.fetcher import HyperliquidMarketDataFetcher
from python.market_data.fetchers.okx.spot.fetcher import OKXSpotMarketDataFetcher
from python.market_data.fetchers.okx.perp.fetcher import OKXPerpMarketDataFetcher
from python.market_data.fetchers.bybit.spot.fetcher import BybitSpotMarketDataFetcher
from python.market_data.fetchers.bybit.perp.fetcher import BybitPerpMarketDataFetcher

market_data_fetchers = [
    HyperliquidMarketDataFetcher,
    OKXSpotMarketDataFetcher,
    OKXPerpMarketDataFetcher,
    BybitSpotMarketDataFetcher,
    BybitPerpMarketDataFetcher
]
