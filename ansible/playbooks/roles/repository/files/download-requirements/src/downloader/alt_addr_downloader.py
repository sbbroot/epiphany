from pathlib import Path
from src.downloader.base_downloader import BaseDownloader


class AltAddrDownloader(BaseDownloader):
    """
    Requirements with provided alternative secondary address.
    """

    def download(self, requirement: str,
                       requirement_file: Path,
                       root_key: str,
                       sub_key: str = None,
                       additional_args: dict = None):
        """
        Download `requirement` as `requirement_file` and compare checksums.

        :param requirement: an entry from the requirements corresponding to the downloaded file
        :param requirement_file: existing requirement file
        :param root_key: primary or secondary root key
        :param sub_key: optional keys for the `requirement` such as `url`
        :param additional_args: optional arguments passed to `download_func`
        :raises:
            :class:`ChecksumMismatch`: can be raised on failed checksum
        """
        req = self._requirements[requirement][root_key]
        addr = req[sub_key] if sub_key else req
        self._download(req, addr, requirement_file, additional_args)
