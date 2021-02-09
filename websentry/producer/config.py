import logging
import os
from typing import List
from websentry.commons import AbstractConfig


class ProducerConfig(AbstractConfig):
    """
    Wrapper class for config options that might be
    """

    def __init__(self):
        self.__init_logging()

    def __init_logging(self):
        logging.basicConfig(level=self.logging_level)

    @property
    def logging_level(self) -> str:
        return self.env_str('WEBSENTRY_LOGLEVEL', 'DEBUG')

    @property
    def urls(self) -> List[str]:
        sites_str: str = self.env_str(
            'WEBSENTRY_SITES', 'https://google.com,https://aiven.io')
        return [u for u in sites_str.split(',')]

    @property
    def check_interval(self) -> int:
        return self.env_int('WEBSENTRY_INTERVAL', 30)

    @property
    def regexp_pattern(self) -> str:
        return self.env_str('WEBSENTRY_REGEXP', '')
