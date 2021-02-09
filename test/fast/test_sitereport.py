import pytest
from websentry.commons import SiteReport
import json


class TestSiteCheck():

    arg_tuples = [
        ('http://foo.com', 400, 1665, None),
        ('http://localhost', 200, 103, 'It works!')
    ]

    @pytest.mark.parametrize('url,code,response_ms,regexp_match', arg_tuples)
    def test_as_json(self, url, code, response_ms, regexp_match):
        r: SiteReport = SiteReport(
            url=url, code=code, response_ms=response_ms, regexp_match=regexp_match)
        json_str: str = r.as_json()
        parsed = json.loads(json_str)
        assert(url == parsed['url'])
        assert(code == parsed['code'])
        assert(response_ms == parsed['response_ms'])
        assert regexp_match == parsed['regexp_match']
        if regexp_match is None:
            assert parsed['regexp_match'] is None
        else:
            assert regexp_match == parsed['regexp_match']

    @pytest.mark.parametrize('url,code,response_ms,regexp_match', arg_tuples)
    def test_from_json(self, url, code, response_ms, regexp_match):
        json_str = '{{"code": {code}, "url": "{url}", "response_ms": {response_ms}, "regexp_match": {regexp_match}}}'.format(
            code=code, url=url, response_ms=response_ms, regexp_match=f'"{regexp_match}"' if regexp_match is not None else 'null')
        r: SiteReport = SiteReport.from_json(json_str)
        assert code == r.code
        assert response_ms == r.response_ms
        assert url == r.url
        assert regexp_match == r.regexp_match

    @pytest.mark.parametrize('url,code,response_ms,regexp_match', arg_tuples)
    def test_roundtrip(self, url, code, response_ms, regexp_match):
        r: SiteReport = SiteReport(
            url=url, code=code, response_ms=response_ms, regexp_match=regexp_match)
        t: SiteReport = SiteReport.from_json(r.as_json())
        assert r == t
