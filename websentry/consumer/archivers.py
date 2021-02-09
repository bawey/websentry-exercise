from typing import List, Optional

from six import reraise
from websentry.commons.sitereport import SiteReport
from websentry.consumer.config import ConsumerConfig
import psycopg2
import logging
import abc

log = logging.getLogger(__name__)


class AbstractArchiver(abc.ABC):
    def __init__(self, config: ConsumerConfig):
        self._config = config

    @abc.abstractmethod
    def archive(self, report: SiteReport):
        pass


class DBArchiver(AbstractArchiver):
    
    TABLE_NAME = 'log'
    CREATE_TABLE_SQL = '''create table if not exists {table_name}(
        id serial primary key,
        stamp timestamp default timezone('UTC', now()),
        url varchar(128) not null,
        code integer,
        response_ms integer,
        regexp_match text
    );
    '''.format(table_name=TABLE_NAME)

    def __init__(self, config: ConsumerConfig):
        super().__init__(config)
        self._dbc = None

    def archive(self, report: SiteReport, encountered_errors: Optional[set] = None):
        log.info(f'Archiving {report}')
        try:
            self._execute_sql(f'insert into {self.TABLE_NAME}(url, code, response_ms, regexp_match) values (%s, %s, %s, %s)',
                              (report.url, report.code, report.response_ms, report.regexp_match))
        except Exception as e:
            log.error(e)
            if encountered_errors is None:
                encountered_errors = set()
            if f'relation "{self.TABLE_NAME}" does not exist' in str(e) and str(e) not in encountered_errors:
                log.error('Will attempt a recovery table creation')
                encountered_errors.add(str(e))
                self._dbc.rollback()
                self._execute_sql(self.CREATE_TABLE_SQL)
                self.archive(report, encountered_errors=encountered_errors)
            else:
                reraise

    def _execute_sql(self, sql: str, params: tuple = None) -> List[tuple]:
        result = []
        if self._dbc is None or self._dbc.closed:
            self._dbc = psycopg2.connect(
                host=self._config.database_host,
                port=self._config.database_port,
                user=self._config.database_user,
                database=self._config.database_name,
                password=self._config.database_password)
        with self._dbc.cursor() as cursor:
            cursor.execute(sql, params)
            if sql.strip().lower().startswith('insert'):
                result.append((cursor.lastrowid,))
            elif sql.strip().lower().startswith('select'):
                for record in cursor:
                    result.append(record)
        self._dbc.commit()
        return result
