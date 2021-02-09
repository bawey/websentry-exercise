import abc
import logging
from typing import Iterable, Optional
from pykafka import KafkaClient, SslConfig, Topic
from pykafka.exceptions import SocketDisconnectedError, LeaderNotAvailable
from websentry.producer.config import ProducerConfig
from websentry.commons import SiteReport

log = logging.getLogger(__name__)


class AbstractDispatcher(abc.ABC):

    def __init__(self, config: ProducerConfig):
        self._config = config

    def dispatch(self, event: SiteReport):
        self.dispatch_all([event])

    @abc.abstractmethod
    def dispatch_all(self, events: Iterable[SiteReport]):
        pass


class KafkaDispatcher(AbstractDispatcher):

    def __init__(self, config: ProducerConfig):
        super().__init__(config)
        self._ssl_config = None
        self._client = None

    @property
    def ssl_config(self) -> SslConfig:
        if self._ssl_config is None:
            self._ssl_config = SslConfig(cafile=self._config.cafile,
                                         certfile=self._config.certfile,
                                         keyfile=self._config.keyfile)
        return self._ssl_config

    @property
    def client(self) -> KafkaClient:
        if self._client is None:
            self._client = KafkaClient(hosts=self._config.kafka_hosts,
                                       ssl_config=self.ssl_config)
        return self._client

    @property
    def topic(self) -> Optional[Topic]:
        return self.client.topics[self._config.kafka_topic]

    def dispatch_all(self, events: Iterable[SiteReport]):
        log.info(self.client.topics)
        with self.topic.get_producer() as producer:
            event: SiteReport
            for event in events:
                message: str = event.as_json()
                log.debug(message)
                encoded_message: bytes = message.encode(
                    self._config.message_encoding)
                try:
                    producer.produce(encoded_message)
                except (SocketDisconnectedError, LeaderNotAvailable) as e:
                    # error handling after: https://pykafka.readthedocs.io/en/latest/usage.html#consumer-patterns
                    log.warning(e)
                    producer.stop()
                    producer.start()
                    producer.produce(encoded_message)
