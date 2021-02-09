from json.decoder import JSONDecodeError
from typing import Dict, Generator, Iterator, Optional
from pykafka.client import KafkaClient
from pykafka.common import OffsetType
from pykafka.connection import SslConfig
from pykafka.simpleconsumer import SimpleConsumer
from pykafka.topic import Topic
from pykafka.protocol.message import Message
from websentry.consumer.config import ConsumerConfig
from websentry.commons import SiteReport
from pykafka.exceptions import SocketDisconnectedError
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Consumer():
    def __init__(self, config: ConsumerConfig):
        self._config = config
        self._client = None
        self._ssl_config = None
        self._topic = None
        self._consumer = None

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
    def topic(self) -> Topic:
        if self._topic is None:
            topic = self.client.topics[self._config.kafka_topic]
            if isinstance(topic, Topic):
                self._topic = topic
                logging.debug(f'Partition: {topic.partitions[0]}')
                logging.debug(
                    f'Earliest offset: {topic.earliest_available_offsets()[0]}')
                logging.debug(
                    f'Latest offset: {topic.latest_available_offsets()[0]}')
            else:
                raise ValueError(
                    f'Did not find the expected topic {self._config.kafka_topic}')
        return self._topic

    @property
    def simple_consumer(self) -> SimpleConsumer:
        if self._consumer is None:
            self._consumer = self.topic.get_simple_consumer(
                consumer_group=self._config.consumer_group_name, auto_offset_reset=OffsetType.EARLIEST)
        return self._consumer

    def unpack_message(self, message: Message) -> Optional[SiteReport]:
        log.debug(f'Message received: {message.value}')
        try:
            return SiteReport.from_json(message.value.decode(self._config.message_encoding))
        except JSONDecodeError as error:
            log.warning(f'Failed to decode should-be JSON: {message.value}')
            log.error(error)

    def fetch(self) -> Optional[SiteReport]:
        """
        Wrapping this in a an extra method for an easy one-off / daemon modes handling
        """
        topic = self.client.topics[self._config.kafka_topic]
        if isinstance(topic, Topic):
            message: Optional[Message] = None
            try:
                message = self.simple_consumer.consume()
            except (SocketDisconnectedError) as e:
                log.warning(e)
                # error handling after: https://pykafka.readthedocs.io/en/latest/usage.html#consumer-patterns
                self.simple_consumer.stop()
                self.simple_consumer.start()
                message = self.simple_consumer.consume()
            if isinstance(message, Message):
                return self.unpack_message(message)

    def start(self) -> Iterator[Optional[SiteReport]]:
        first_fetch = True
        while self._config.daemon_mode or first_fetch:
            try:
                first_fetch = False
                yield self.fetch()
                self.simple_consumer.commit_offsets()
            except Exception as e:
                log.error(e)
