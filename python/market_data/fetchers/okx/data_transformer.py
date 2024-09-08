"""
Data transformer for OKX spot market data
"""

from typing import List
import logging
import json

from python.types.tick_record import TickRecord, UpdateType


class OKXOrderBookDataTransformer:
    """
    Class for transforming WS / Order book channel data from OKX to TickRecord
    """

    @staticmethod
    def transform_json_message(message, receive_timestamp: int) -> List[TickRecord]:
        """
        Transform the json message from OKX from WS / Order book channel to TickRecord
        """
        message = json.loads(message)
        if message.get('event') == 'subscribe':
            return []

        try:
            if message['action'] == 'snapshot':
                return OKXOrderBookDataTransformer.transform_message_data_for_update_type(
                    message['data'],
                    'new',
                    receive_timestamp
                )
            if message['action'] == 'update':
                return OKXOrderBookDataTransformer.transform_message_data_for_update_type(
                    message['data'],
                    'update',
                    receive_timestamp
                )

            logging.error("Unknown action: %s", message['action'])
        # pylint: disable=broad-except
        except Exception as e:
            logging.error("Error %s while transforming message %s", e, message)
        return []

    @staticmethod
    def transform_message_data_for_update_type(
        data_list,
        update_type: UpdateType,
        receive_timestamp: int
    ) -> List[TickRecord]:
        """
        Common logic to transform the data list to TickRecord 
        for both new and update types
        """
        records = []
        for data in data_list:
            for bid_data in data['bids']:
                record = TickRecord(
                    receive_timestamp=receive_timestamp,
                    exchange_timestamp=int(data['ts']),
                    tick_type='bid',
                    update_type=update_type,
                    price=float(bid_data[0]),
                    size=float(bid_data[1])
                )
                records.append(record)
            for ask_data in data['asks']:
                record = TickRecord(
                    receive_timestamp=receive_timestamp,
                    exchange_timestamp=int(data['ts']),
                    tick_type='ask',
                    update_type=update_type,
                    price=float(ask_data[0]),
                    size=float(ask_data[1])
                )
                records.append(record)
        return records
