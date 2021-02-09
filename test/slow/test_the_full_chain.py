from websentry.consumer.config import ConsumerConfig
from websentry.consumer.archivers import DBArchiver
from websentry.consumer.consumer import Consumer
from websentry.producer import main as producer_main, Sentry, AbstractDispatcher, KafkaDispatcher
from websentry.consumer import main as consumer_main, Consumer, AbstractArchiver, DBArchiver
from websentry.producer.config import ProducerConfig
import pytest
import itertools


@pytest.mark.usefixtures('init_db')
class TestTheFullChain():
    prod_config: ProducerConfig = ProducerConfig()
    cons_config: ConsumerConfig = ConsumerConfig()
    sentry: Sentry = Sentry(prod_config)
    dispatcher: AbstractDispatcher = KafkaDispatcher(prod_config)
    archiver: DBArchiver = DBArchiver(cons_config)
    consumer: Consumer = Consumer(cons_config)

    def count_stored(self) -> int:
        rows = self.archiver._execute_sql('select count(*) from log')
        return rows[0][0]

    def test_the_full_chain(self):
        assert self.cons_config.daemon_mode is False
        assert -1 == self.prod_config.check_interval
        assert self.cons_config.daemon_mode is False

        sites_count: int = len(self.prod_config.urls)
        initially_stored = self.count_stored()
        producer_main(self.prod_config, sentries=[
                      self.sentry], dispatchers=[self.dispatcher])
        for _ in itertools.repeat(None, sites_count):
            # in non-damonized mode the consumer will only fetch one message at a time
            consumer_main(self.cons_config, archiver=self.archiver)
        assert (initially_stored + sites_count) == self.count_stored()
