import os
import abc


class AbstractConfig(abc.ABC):
    def env_bool(self, key: str, default: bool = False) -> bool:
        return default if os.getenv(key, None) is None else bool(int(os.getenv(key, '0')))

    def env_int(self, key: str, default: int = 0) -> int:
        return int(os.getenv(key, '0')) or default

    def env_str(self, key: str, default: str = '') -> str:
        return os.getenv(key, default)

    @property
    def kafka_topic(self) -> str:
        return self.env_str('WEBSENTRY_KAFKA_TOPIC', 'sitecheck')

    @property
    def cafile(self) -> str:
        return self.env_str('WEBSENTRY_KAFKA_CAFILE')

    @property
    def certfile(self) -> str:
        return self.env_str('WEBSENTRY_KAFKA_CERTFILE')

    @property
    def keyfile(self) -> str:
        return self.env_str('WEBSENTRY_KAFKA_KEY')

    @property
    def kafka_hosts(self) -> str:
        return self.env_str('WEBSENTRY_KAFKA_HOSTS', 'kafka-tomekbawej-2d43.aivencloud.com:19663')

    @property
    def message_encoding(self) -> str:
        return self.env_str('WEBSENTRY_MESSAGE_ENCODING', 'utf-8')
