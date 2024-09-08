"""
Enum for exchange names where market data is fetched
"""

from enum import Enum

class ExchangeName(str, Enum):
    """Enum for exchange names"""
    OKX = "OKX"
    BYBIT = "Bybit"
    HYPERLIQUID = "Hyperliquid"
