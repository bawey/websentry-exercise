from websentry.consumer.config import ConsumerConfig
from websentry.consumer.archivers import DBArchiver, AbstractArchiver
from websentry.consumer.consumer import Consumer
from websentry.commons import SiteReport

import logging

__all__ = ['ConsumerConfig', 'AbstractArchiver', 'DBArchiver', 'Consumer']

log = logging.getLogger(__name__)


def main(config: ConsumerConfig = None, consumer: Consumer = None, archiver: AbstractArchiver = None):
    config = config or ConsumerConfig()
    consumer = consumer or Consumer(config=config)
    archiver = archiver or DBArchiver(config=config)
    for report in consumer.start():
        log.debug(f'Received a report: {report}')
        if isinstance(report, SiteReport):
            archiver.archive(report)
