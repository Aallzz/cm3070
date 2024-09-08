"""
Data transformer for Bybit spot market data
"""

from typing import List, Literal
import logging
import json

from python.types.tick_record import TickRecord


BybitResponseType = Literal['snapshot', 'delta']


class BybitOrderBookDataTransformer:
    """
    Class for transforming WS / Order book channel data from Bybit to TickRecord
    """

    @staticmethod
    def transform_json_message(message: str, receive_timestamp: int) -> List[TickRecord]:
        """
        Transform the json message from Bybit from WS / Order book channel to TickRecord
        """
        message = json.loads(message)

        if message.get('op') == 'subscribe':
            if message['success']:
                return []
            logging.error("Subscription failed: %s", message)
            return []

        exchange_timestamp = int(message['ts'])
        if message['type'] == 'snapshot':
            return BybitOrderBookDataTransformer.transform_message_data_for_update_type(
                message['data'],
                'snapshot',
                receive_timestamp,
                exchange_timestamp
            )
        if message['type'] == 'delta':
            return BybitOrderBookDataTransformer.transform_message_data_for_update_type(
                message['data'],
                'delta',
                receive_timestamp,
                exchange_timestamp
            )

        logging.error("Unknown type: %s", message['type'])
        return []

    @staticmethod
    def transform_message_data_for_update_type(
            data,
            response_type: BybitResponseType,
            receive_timestamp: int,
            exchange_timestamp: int
    ) -> List[TickRecord]:
        """
        Common logic to transform the data list to 
        TickRecord for both new and update types
        """
        records = []
        for bid_data in data['b']:
            record = TickRecord(
                receive_timestamp=receive_timestamp,
                exchange_timestamp=exchange_timestamp,
                tick_type='bid',
                update_type='new' if response_type == 'snapshot' else (
                    'delete' if bid_data[1] == 0 else 'update'
                ),
                price=float(bid_data[0]),
                size=float(bid_data[1])
            )
            records.append(record)
        for ask_data in data['a']:
            record = TickRecord(
                receive_timestamp=receive_timestamp,
                exchange_timestamp=exchange_timestamp,
                tick_type='ask',
                update_type='new' if response_type == 'snapshot' else (
                    'delete' if ask_data[1] == 0 else 'update'
                ),
                price=float(ask_data[0]),
                size=float(ask_data[1])
            )
            records.append(record)
        return records
