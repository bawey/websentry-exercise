import logging
from typing import Optional
from websentry.producer.config import ProducerConfig
from websentry.commons import SiteReport
import requests
from requests import Response
import re

log = logging.getLogger(__name__)


class Sentry():
    """
    Class responsible for checking the website and producing a SiteCheck object
    """

    def __init__(self, config: ProducerConfig):
        self._config = config

    def check_site(self, url: str, regexp_pattern: Optional[str] = None) -> SiteReport:
        try:
            response: Response = requests.get(url)
            regexp_match = None
            if regexp_pattern:
                regexp_match = self.check_for_regexp(
                    regexp_pattern, response.text)
            return SiteReport(url=url, code=response.status_code, response_ms=response.elapsed.microseconds//1000,
                              regexp_match=regexp_match)
        except Exception as e:
            log.error(f'Fetching from {url} failed: {e}')
        return SiteReport(url=url, code=0, response_ms=0)

    def check_for_regexp(self, pattern: str, content: str) -> Optional[str]:
        match: Optional[re.Match] = re.search(pattern=pattern, string=content)
        if match:
            if match.groups():
                return ''.join(match.groups())
            return match.group(0)
        return None
