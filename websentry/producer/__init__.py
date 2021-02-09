from typing import List
from websentry.commons.sitereport import SiteReport
from websentry.producer.config import ProducerConfig
from websentry.producer.sentries import Sentry
from websentry.producer.dispatchers import AbstractDispatcher, KafkaDispatcher
import logging
import time

__all__ = ['SiteReport', 'ProducerConfig', 'Sentry', 'KafkaDispatcher', 'AbstractDispatcher']

log = logging.getLogger(__name__)


def main(config: ProducerConfig = ProducerConfig(), sentries: List[Sentry] = None, dispatchers: List[AbstractDispatcher] = None):
    log.debug('producer module launches')
    sentries = sentries or [Sentry(config)]
    dispatchers = dispatchers or [KafkaDispatcher(config)]
    url: str
    go_on: bool = True
    while(go_on):
        go_on = False
        sentry: Sentry
        for sentry in sentries:
            reports: List[SiteReport] = []
            for url in config.urls:
                reports.append(sentry.check_site(url, config.regexp_pattern))
            dispatcher: AbstractDispatcher
            for dispatcher in dispatchers:
                dispatcher.dispatch_all(reports)
        if config.check_interval > 0:
            time.sleep(config.check_interval)
            go_on = True
