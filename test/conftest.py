import pytest
import os
import sys
import pathlib

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent), 'src'))
from common.db.base_engine import BaseEngine  # noqa: #402


@pytest.fixture(scope='session')
def testdb_session():
    """
    SessionスコープでテストDBへのセッションを返す

    DBセッションを確立するのはテスト全体を通して1回のみ
    """
    session = BaseEngine(
        os.environ['POSTGRESQL_USER'],
        os.environ['POSTGRESQL_PASSWORD'],
        os.environ['POSTGRESQL_HOST'],
        os.environ['POSTGRESQL_PORT'],
        os.environ['POSTGRESQL_TEST_DB_NAME'],
    ).get_session()

    yield session

    session.rollback()


@pytest.fixture(scope='function')
def testdb(testdb_session):
    """
    testdb_sessionフィクスチャからDBセッションを受け取り、FunctionスコープでテストDBのロールバックを行う

    DBを用いたテストを行う際は、ロールバックしてから行うことでテストの不変性を保つ
    """
    testdb_session.rollback()
    return testdb_session
