"""
A module to log messages for the MarketDataRecorder class.
"""
import logging
import os

from python.market_data.fetchers.fetcher import MarketDataFetcher

class MarketDataRecorderLogger:
    """
    A class to log messages for the MarketDataRecorder class.
    """

    def __init__(self, fetcher: MarketDataFetcher):
        logging.basicConfig(filename="logs.txt",
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO,
                            force=True
                            )

        self.fetcher = fetcher
        self.logger = logging.getLogger("MarketDataRecorder")

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

    def log_prefix(self):
        """
        Create a log prefix based on the fetcher class and the current process id.
        """
        # pylint: disable=consider-using-f-string
        return "[%s:%s:%s:%d]" % (
            self.fetcher.exchange_name(),
            self.fetcher.supported_asset_type(),
            self.fetcher.instrument,
            os.getpid()
        )
