"""
A script to start a process for each market data fetcher to record market data to a file.
"""
import os
import datetime
from multiprocessing import Process
import asyncio

import signal
from python.market_data.fetchers import market_data_fetchers
from python.types.tick_record import TickRecord
from python.market_data.fetchers.fetcher import MarketDataFetcher
from python.market_data.data_recorder_logger import MarketDataRecorderLogger


from python.market_data.data_recorder_process_locker import DataRecorderProcessLocker


def create_market_data_csv_path(
        market_data_fetcher: MarketDataFetcher,
):
    """Create directory path based on the fetcher class and current time."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    current_time = datetime.datetime.now()

    directory_path = os.path.join(
        "data",
        "server_one",
        f"{current_time.year}-{months[current_time.month-1]}",
        market_data_fetcher.exchange_name(),
        market_data_fetcher.supported_asset_type(),
        market_data_fetcher.instrument
    )
    os.makedirs(directory_path, exist_ok=True)
    return os.path.join(directory_path, f"{current_time.day}.csv")


def next_day_start_time(time: datetime.datetime) -> datetime.datetime:
    """Calculate the start time of the next day."""
    return (time + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


class MarketDataRecorder:
    """
    A class to record market data to a file from a fetcher listening to the market data.
    """

    def __init__(self, fetcher: MarketDataFetcher, end_time: datetime.datetime):
        self.fetcher = fetcher
        self.recorder_start_time = datetime.datetime.now()
        self.recorder_end_time = end_time
        self.logger = MarketDataRecorderLogger(fetcher)
        self.file_path = create_market_data_csv_path(fetcher)

        self.recording_lock = DataRecorderProcessLocker(self.file_path)

    def start_recording(self):
        """
        Blocking function to start recording market data 
        to a file from a fetcher listening to the market data.
        The recording will stop at the recorder_end_time.
        """

        with open(self.file_path, "a", encoding='utf-8') as market_data_file:
            if os.path.getsize(self.file_path) == 0:
                market_data_file.write(TickRecord.csv_header())

            timeout = (self.recorder_end_time -
                       self.recorder_start_time).total_seconds()

            self.logger.log_info(
                f"Start recording market data to file {self.file_path} with timout {timeout}s")

            asyncio.run(
                asyncio.wait_for(
                    self.fetcher.listen_and_process(
                        lambda record: market_data_file.write(
                            record.to_csv_line() + "\n")
                    ),
                    timeout=timeout
                )
            )

            self.logger.log_info(
                "Recording finished without timout exception. This is suspicious.")

    def start_process_safe_recording(self):
        """
        Start a recording process with a lock to prevent multiple processes 
        from recording the same market data.
        """
        signal.signal(signal.SIGTERM, self.sigterm_handler)

        # pylint: disable=broad-except
        try:
            lock_result = self.recording_lock.lock()

            if not lock_result:
                self.logger.log_info(
                    "Recording is already in progress, exiting...")
                return

            self.logger.log_info("Initiate recording market data...")
            self.start_recording()

        except asyncio.TimeoutError as e:
            self.logger.log_info(f"Recording timeout: {e}")

        except Exception as e:
            # It won't catch user interrupt signal, they are handled by the signal handler
            self.logger.log_error(f"Error in data fetching process: {e}")

        finally:
            self.recording_lock.unlock()

            self.logger.log_info(
                "Recording finished, starting a new recording process...")

            MarketDataRecorder(
                self.fetcher,
                next_day_start_time(datetime.datetime.now())
            ).start_process()

            self.logger.log_info("Exiting the recording process...")

            os._exit(0)

    def start_process(self):
        """
        Start a new process to record market data.
        """
        process = Process(target=self.start_process_safe_recording)
        process.start()
        self.logger.log_info(
            f"New recording process started with pid {process.pid}")

    def sigterm_handler(self, _sig, _frame):
        """
        Signal handler for SIGTERM to unlock the recording lock and exit the recording process.
        """
        self.logger.log_info("Received SIGTERM, exiting...")
        self.recording_lock.unlock()
        self.logger.log_info("Exit")
        os._exit(0)


if __name__ == "__main__":
    for fetcher_class in market_data_fetchers:
        for instrument in fetcher_class.supported_instruments_for_test():
            data_fetcher = fetcher_class(instrument)
            data_recorder = MarketDataRecorder(
                data_fetcher, next_day_start_time(datetime.datetime.now()))
            data_recorder.start_process()
