from websentry.producer.config import ProducerConfig
import pytest
from websentry.producer import Sentry
from websentry.commons import SiteReport


class TestSentry():
    config: ProducerConfig = ProducerConfig()
    sentry: Sentry = Sentry(config)

    @pytest.mark.parametrize('text, pattern, expected', [
        ('<div><span>42</span><span>FooBar</span></div>',
         r'(?:<span>)([A-Za-z]+)(?:</span>)', 'FooBar'),
        ('<div><span>42</span><span>FooBar</span></div>',
         r'(?:<span>)FooBar(?:</span>)', '<span>FooBar</span>'),
        ('<div><span>FootBar</span></div>', r'(?:<span>)FooBar(?:</span>)', None)
    ])
    def test_regexp_matching(self, text: str, pattern: str, expected: str):
        assert expected == self.sentry.check_for_regexp(pattern, text)

    def test_googling(self, url='https://google.com'):
        report: SiteReport = self.sentry.check_site(
            url, regexp_pattern=r'.')
        assert 200 == report.code
        assert 10000 > report.response_ms > 0
        assert url == report.url
        assert report.regexp_match is not None

    @pytest.mark.parametrize('url, expected_code', [
        ('https://google.com/404', 404),
        ('http://nonexistent', 0)
    ])
    def test_broken_urls(self, url: str, expected_code: int):
        report: SiteReport = self.sentry.check_site(url)
        assert expected_code == report.code
        assert url == report.url
