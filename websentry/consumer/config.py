import logging
import os
from websentry.commons import AbstractConfig


class ConsumerConfig(AbstractConfig):

    def __init__(self):
        self.__init_logging()

    def __init_logging(self):
        logging.basicConfig(level=self.logging_level)

    @property
    def logging_level(self):
        return self.env_str('WEBSENTRY_CONSUMER_LOGLEVEL', 'DEBUG')

    @property
    def daemon_mode(self) -> bool:
        return self.env_bool('WEBSENTRY_CONSUMER_ENABLE_DAEMON', True)

    @property
    def consumer_group_name(self) -> str:
        return self.env_str('WEBSENTRY_CONSUMER_GROUP', 'healthcheck-relay')

    @property
    def database_name(self) -> str:
        return self.env_str('WEBSENTRY_DATABASE_NAME', 'websentry')

    @property
    def database_host(self) -> str:
        return self.env_str('WEBSENTRY_DATABASE_HOST', 'localhost')

    @property
    def database_port(self) -> int:
        return self.env_int('WEBSENTRY_DATABASE_PORT', 5432)

    @property
    def database_user(self) -> str:
        return self.env_str('WEBSENTRY_DATABASE_USER', 'websentry')

    @property
    def database_password(self) -> str:
        return self.env_str('WEBSENTRY_DATABASE_PASSWORD', 'websentry')
