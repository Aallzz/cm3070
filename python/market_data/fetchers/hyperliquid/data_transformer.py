"""
HyperliquidDataTransformer class, which is responsible for transforming Hyperliquid data types
"""

from typing import List
import time
import json

from python.types.tick_record import TickRecord, TickType


class HyperliquidDataTransformer:
    """
    Class to transform Hyperliquid data types into TickRecord
    """

    def __init__(self):
        pass

    @staticmethod
    def transform_json_message(
        data: str,
        recieve_timestamp: int
    ) -> List[TickRecord]:
        """
        Transform a l2book message into a list of TickRecord
        """
        message = json.loads(data)

        if message.get('channel') == 'subscriptionResponse':
            return []

        exchange_time = message["data"]["time"]
        bids = HyperliquidDataTransformer.transform_l2book_side(
            message["data"]["levels"][0], "bid", recieve_timestamp, exchange_time
        )
        asks = HyperliquidDataTransformer.transform_l2book_side(
            message["data"]["levels"][1], "ask", recieve_timestamp, exchange_time)
        return bids + asks

    @staticmethod
    def transform_l2book_side(levels,
                              tick_type: TickType,
                              recieve_timestamp: int,
                              exchange_time: int
                              ) -> List[TickRecord]:
        """
        Transform a l2book side info into a list of TickRecord
        """
        results = []
        for level_info in levels:
            results.append(TickRecord(
                receive_timestamp=recieve_timestamp,
                exchange_timestamp=exchange_time,
                tick_type=tick_type,
                update_type="new",
                price=float(level_info['px']),
                size=float(level_info['sz'])
            ))
        return results
