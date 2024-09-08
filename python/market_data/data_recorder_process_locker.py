"""
A module to lock the recording process using file as a lock regestry
"""

import fcntl


class DataRecorderProcessLocker:
    """
    A class to lock the recording process using file as a lock regestry
    """

    def __init__(self, market_data_file_path: str):
        self.market_data_file_path = market_data_file_path
        self.processes_registry_file = "process_registry.txt"

    def lock(self) -> bool:
        """
        Lock the recording process using file as a lock regestry to 
        prevent multiple processes from recording the same market data.
        """
        with open(self.processes_registry_file, "a+", encoding='utf-8') as f:
            fcntl.flock(f, fcntl.LOCK_EX)

            f.seek(0)
            contents = f.readlines()
            contents = [line.strip() for line in contents]

            if self.market_data_file_path in contents:
                fcntl.flock(f, fcntl.LOCK_UN)
                return False

            f.write(self.market_data_file_path + "\n")
            fcntl.flock(f, fcntl.LOCK_UN)

        return True

    def unlock(self):
        """
        Unlock the recording process by removing the file from the lock registry.
        """
        with open(self.processes_registry_file, "r+", encoding='utf-8') as f:
            fcntl.flock(f, fcntl.LOCK_EX)

            f.seek(0)
            contents = f.readlines()
            contents = [line.strip() for line in contents]

            if self.market_data_file_path in contents:
                contents.remove(self.market_data_file_path)
                f.seek(0)
                f.truncate()
                f.write("\n".join(contents) + "\n")

            fcntl.flock(f, fcntl.LOCK_UN)
