import pytest
import os
import sys
import pathlib
import pandas as pd

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent), 'main'))
from common.logger.common_logger import CommonLogger  # noqa: #402
from common.db.base_engine import BaseEngine  # noqa: #402
from stock.dto.stock_dto import Company, StockPrice  # noqa: #402


@pytest.fixture(scope='session')
def testdb_session():
    """
    SessionスコープでテストDBへのセッションを返す

    DBセッションを確立するのはテスト全体を通して1回のみ
    """
    session = BaseEngine(
        os.environ['POSTGRES_TEST_USER'],
        os.environ['POSTGRES_TEST_PASSWORD'],
        os.environ['POSTGRES_TEST_HOST'],
        os.environ['POSTGRES_TEST_PORT'],
        os.environ['POSTGRES_TEST_DB'],
    ).get_session()

    yield session

    session.rollback()


@pytest.fixture(scope='function')
def testdb(testdb_session):
    """
    testdb_sessionフィクスチャからDBセッションを受け取り、FunctionスコープでテストDBのロールバックを行う

    DBを用いたテストを行う際は、ロールバックしてから行うことでテストの独立性を保つ
    """
    testdb_session.rollback()
    return testdb_session


@pytest.fixture(scope='function')
def application_logger():
    """
    アプリケーション内で共有するロガー。環境変数から出力パスを渡す。
    """
    logger = CommonLogger().get_application_logger(
        os.environ['APPLICATION_LOG_PATH'],
        __name__,
    )
    return logger


# テスト用の事前準備データはファイルを跨いで使うことが多いので、conftest.pyにまとめる
# 但しテストによって必要なデータ群は異なるので、DBにINSERTする処理は各テストファイルに記載する

# CSV->DTO変換関数
def company_csv_to_dto(csv_path):
    """
    CSVをpandasデータフレームでロードし、DTOに変換するため関数

    companyテーブルのデータをcsvをデータソースとして事前準備する各フィクスチャ内で使用する
    """
    dtypes = {'company_id': 'str', 'company_name': 'str',
              'stock_code': 'str', 'country_code': 'str',
              'listed_market': 'str', 'longitude': 'float',
              'latitude': 'float'}
    try:
        test_data = pd.read_csv(csv_path, encoding='utf-8', dtype=dtypes)
    except UnicodeEncodeError:
        test_data = pd.read_csv(csv_path, encoding='cp-932', dtype=dtypes)

    companies = []
    for idx in test_data.index:
        company = Company()
        company.company_id = test_data.at[idx, 'company_id']
        company.company_name = test_data.at[idx, 'company_name']
        company.stock_code = test_data.at[idx, 'stock_code']
        company.country_code = test_data.at[idx, 'country_code']
        company.listed_market = test_data.at[idx, 'listed_market']
        company.foundation_date = test_data.at[idx, 'foundation_date']
        company.longitude = test_data.at[idx, 'longitude']
        company.latitude = test_data.at[idx, 'latitude']
        companies.append(company)

    return companies


def stock_price_csv_to_dto(csv_path):
    """
    CSVをpandasデータフレームでロードし、DTOに変換するため関数

    stock_priceテーブルをcsvをデータソースとして事前準備する各フィクスチャ内で使用する
    """
    dtypes = {'company_id': 'str', 'open_price': 'float',
              'high_price': 'float', 'low_price': 'float',
              'close_price': 'float', 'volume': 'float'}
    try:
        test_data = pd.read_csv(csv_path,
                                encoding='utf-8',
                                dtype=dtypes,
                                parse_dates=['date'])
    except UnicodeEncodeError:
        test_data = pd.read_csv(csv_path,
                                encoding='cp-932',
                                dtype=dtypes,
                                parse_dates=['date'])

    stock_prices = []
    for idx in test_data.index:
        stock_price = StockPrice()
        stock_price.company_id = test_data.at[idx, 'company_id']
        stock_price.date = test_data.at[idx, 'date'].date()
        stock_price.open_price = test_data.at[idx, 'open_price']
        stock_price.high_price = test_data.at[idx, 'high_price']
        stock_price.low_price = test_data.at[idx, 'low_price']
        stock_price.close_price = test_data.at[idx, 'close_price']
        stock_price.volume = test_data.at[idx, 'volume']
        stock_prices.append(stock_price)

    return stock_prices


# 事前準備データ(DB)
@pytest.fixture(scope='session')
def company_test_data_001():
    """
    Resourcesフォルダからテスト用に事前にDBに格納するcompanyテーブルのダミーデータ

    CSVからデータをロードし、DTOのリストとして変換する.\n
    将来的に本番データを使ってsqldumpから事前にデータを準備することも検討に入れる.
    """
    csv_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'prepare',
        'company_test_data_001.csv'
    )

    return company_csv_to_dto(csv_path)


@pytest.fixture(scope='session')
def stock_prices_test_data_001():
    """
    Resourcesフォルダからテスト用に事前にDBに格納するstock_priceテーブルのダミーデータ

    CSVからデータをロードし、DTOのリストとして変換する.\n
    将来的に本番データを使ってsqldumpから事前にデータを準備することも検討に入れる.
    """
    csv_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'prepare',
        'stock_prices_test_data_001.csv'
    )

    return stock_price_csv_to_dto(csv_path)


# テスト用データ
@pytest.fixture(scope='session')
def test_common_dao_delsert_data():
    """
    test_common_dao.py::TestDelsertで使用するテストデータ
    """
    csv_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'common',
        'test_common_dao_test_delsert_data.csv'
    )

    return stock_price_csv_to_dto(csv_path)


@pytest.fixture(scope='session')
def test_common_dao_upsert_data():
    """
    test_common_dao.py::TestUpsertで使用するテストデータ
    """
    csv_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'common',
        'test_common_dao_test_upsert_data.csv'
    )

    return stock_price_csv_to_dto(csv_path)
