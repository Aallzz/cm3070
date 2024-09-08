"""
Abstract class for market data fetchers
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Callable, List
import time
import json

import aio_pika
from okx.websocket.WebSocketFactory import WebSocketFactory

from python.market_data.fetchers.fetcher_logger import MarketDataFetcherLogger
from python.types.tick_record import TickRecord
from python.types.enums.asset_type import AssetType
from python.types.enums.exchange_name import ExchangeName


class MarketDataFetcher(ABC):
    """
    Abstract class for market data fetchers that listens to the specified 
    for the instrument on the exchange specified in children and processed by
    process function passed by the fetcher users (for example cron job that
    writes to files)
    """

    def __init__(self, instrument: str):
        self.instrument = instrument
        self.queue_name = f"{self.exchange_name()}.{self.supported_asset_type()}.{instrument}"

        self.logger = MarketDataFetcherLogger(
            self.exchange_name(),
            self.supported_asset_type(),
            instrument
        )

    async def run(self, process: Callable[[TickRecord], None]):
        """
        Run the fetcher and process the data courutines
        """
        self.logger.log_info("Start fetching and processing market data.")

        await asyncio.gather(
            asyncio.create_task(self.fetch()),
            asyncio.create_task(self.process(process))
        )

        self.logger.log_info("Stop fetching and processing market data.")

    async def fetch(self):
        """
        Listen to the market data and process it
        """
        connection = await aio_pika.connect_robust()
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(self.queue_name, durable=True)

            ws_factory = WebSocketFactory(self.websocket_url())
            ws = await ws_factory.connect()

            await ws.send(self.subscription_arguments_str())

            self.logger.log_info(
                "Start infinite loop to fetch data from websocket.")
            while True:
                ws_data = await ws.recv()
                self.logger.log_with_sampling(
                    f"Received data from websocket: {ws_data}"
                )
                ws_data_with_timestamp = json.dumps({
                    "data": ws_data,
                    "receive_timestamp": round(time.time() * 1000)
                })
                message = aio_pika.Message(
                    body=ws_data_with_timestamp.encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                await channel.default_exchange.publish(
                    message,
                    routing_key=self.queue_name
                )

    async def process(self, process: Callable[[TickRecord], None]):
        """
        Process the data from the queue
        """
        connection = await aio_pika.connect_robust()
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.queue_name, durable=True)

            async def transform_and_process(message: aio_pika.abc.AbstractIncomingMessage) -> None:
                try:
                    async with message.process():
                        self.logger.log_with_sampling(
                            f"Received data from queue: {message.body}")
                        ws_data_with_timestamp = json.loads(message.body)
                        records = self.transform_json_to_tick_record(
                            message=ws_data_with_timestamp['data'],
                            receive_timestamp=ws_data_with_timestamp["receive_timestamp"]
                        )
                        for record in records:
                            process(record)
                # pylint: disable=broad-except
                except Exception as e:
                    self.logger.log_error(f"Error processing message: {e}")

            self.logger.log_info("Start consuming data from the queue.")
            await queue.consume(transform_and_process)
            try:
                # Wait until terminate
                await asyncio.Future()
            finally:
                await connection.close()
            self.logger.log_info("Stop consuming data from the queue.")

    @abstractmethod
    def transform_json_to_tick_record(self, message: str, receive_timestamp: int) -> List[TickRecord]:
        """
        Transform JSON message to tick record
        """

    @abstractmethod
    def subscription_arguments_str(self) -> str:
        """
        Subscription arguments for the websocket
        """

    @abstractmethod
    def websocket_url(self) -> str:
        """
        Instruments supported by the fetcher
        """

    async def listen_and_process(self, process: Callable[[TickRecord], None]):
        """
        Listen to the market data and process it
        """
        await self.run(process)

    @staticmethod
    @abstractmethod
    def supported_instruments() -> List[str]:
        """
        Instruments supported by the fetcher
        """

    @staticmethod
    @abstractmethod
    def supported_instruments_for_test() -> List[str]:
        """
        Instruments supported by the fetcher for test runs
        """

    @staticmethod
    @abstractmethod
    def supported_asset_type() -> AssetType:
        """
        Instruments supported by the fetcher
        """

    @staticmethod
    @abstractmethod
    def exchange_name() -> ExchangeName:
        """
        Exchange name
        """
