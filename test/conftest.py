from websentry.consumer.config import ConsumerConfig
from websentry.consumer.archivers import DBArchiver
import pytest
import psycopg2


DROP_TABLE_SQL = 'drop table if exists log'


@pytest.fixture(scope='class')
def init_db():
    config: ConsumerConfig = ConsumerConfig()

    conn = psycopg2.connect(host=config.database_host, port=config.database_port,
                            user=config.database_user, database=config.database_name, password=config.database_password)
    cur = conn.cursor()
    cur.execute(DROP_TABLE_SQL)
    cur.execute(DBArchiver.CREATE_TABLE_SQL)
    cur.close()
    conn.commit()
    conn.close()


@pytest.fixture(scope='function')
def drop_table():
    config: ConsumerConfig = ConsumerConfig()
    conn = psycopg2.connect(host=config.database_host, port=config.database_port,
                            user=config.database_user, database=config.database_name, password=config.database_password)
    cur = conn.cursor()
    cur.execute(DROP_TABLE_SQL)
    cur.close()
    conn.commit()
    conn.close()
