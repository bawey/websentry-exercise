from typing import List
from websentry.consumer import ConsumerConfig, DBArchiver
from websentry.commons import SiteReport
import pytest


@pytest.mark.usefixtures('init_db')
class TestDBArchiver():
    config: ConsumerConfig = ConsumerConfig()
    archiver: DBArchiver = DBArchiver(config)
    reports: List[SiteReport] = [
        SiteReport('http://localhost', 200, 1102,
                   'DB greetings from the tests!'),
        SiteReport('https://google.com', 200, 1102, None),
        SiteReport('https://google.com', 200, 1302, 'With some regex hit'),
        SiteReport('http://xyz', 0, 0, None)
    ]

    def get_last(self) -> tuple:
        query: str = 'select * from log order by id desc limit 1'
        rows = self.archiver._execute_sql(query)
        assert 1 == len(rows)
        return rows[0]

    def count_stored(self) -> int:
        return self.archiver._execute_sql('select count(*) from log')[0][0]

    @pytest.mark.parametrize('report', reports)
    def test_db_insertion(self, report: SiteReport):
        pre_stored: int = self.count_stored()
        self.archiver.archive(report)
        last = self.get_last()
        assert report.url in last
        assert report.code in last
        assert report.regexp_match in last
        assert report.response_ms in last
        assert (pre_stored + 1) == self.count_stored()

    def test_automatic_table_creation(self, drop_table, report=reports[0]):
        self.archiver.archive(report)
        assert 1 == self.count_stored()
