"""
A module to log messages for the MarketDataRecorder class.
"""
import logging
import os
import random

from python.types.enums.asset_type import AssetType

class MarketDataFetcherLogger:
    """
    A class to log messages for the MarketFetcherLogger class.
    """

    def __init__(self, exchange_name: str, supported_asset_type: AssetType, instrument: str):
        self.exchange_name = exchange_name
        self.supported_asset_type = supported_asset_type
        self.instrument = instrument

        self.logger = logging.getLogger("MarketDataFetcher")

    def log_info(self, message):
        """
        Log an info message with a prefix.
        """
        self.logger.info("%s %s", self.log_prefix(), message)

    def log_error(self, message):
        """
        Log an error message with a prefix.
        """
        self.logger.error("%s %s", self.log_prefix(), message)


    def log_with_sampling(self, message, sample_rate=0.00005):
        """
        Log a message with a sampling rate.
        """
        if random.random() < sample_rate:
            self.logger.info("%s %s", self.log_prefix("sampled"), message)

    def log_prefix(self, extra_message=""):
        """
        Create a log prefix based on the fetcher class and the current process id.
        """
        # pylint: disable=consider-using-f-string
        return "[%s:%s:%s:%d%s]" % (
            self.exchange_name,
            self.supported_asset_type,
            self.instrument,
            os.getpid(),
            f":{extra_message}" if extra_message else ""
        )
