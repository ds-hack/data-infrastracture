import os
import sys
import pathlib
import pytest
import pandas as pd

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'src'))
from common.db.common_dao import CommonDao  # noqa: #402
from stock.dto.stock_dto import StockPrice  # noqa: #402


@pytest.fixture(session='function')
def stock_prices_test_data_001():
    """
    Resourcesフォルダからテスト用に事前にDBに格納するデータ

    CSVからデータをロードし、DTOのリストとして変換する.\n
    将来的に本番データを使ってsqldumpから事前にデータを準備することも検討に入れる.
    """
    csv_path = './test/resources/stock_prices_test_data_001.csv'
    try:
        test_data = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeEncodeError:
        test_data = pd.read_csv(csv_path, encoding='cp-932')

    stock_prices = []
    for idx in test_data.index:
        stock_price = StockPrice()
        stock_price.company_id = test_data.at[idx, 'company_id']
        stock_price.date = test_data.at[idx, 'date']
        stock_price.open_price = test_data.at[idx, 'open_price']
        stock_price.high_price = test_data.at[idx, 'high_price']
        stock_price.low_price = test_data.at[idx, 'low_price']
        stock_price.close_price = test_data.at[idx, 'close_price']
        stock_price.volume = stock_price.at[idx, 'volume']
        stock_prices.append(stock_price)

    return stock_prices


@pytest.fixture(session='function', name='session_001')
def db_with_test_data_001(testdb, stock_prices_test_data_001):
    """
    CommonDaoクラスのテストに使用するデータをDBに格納し、テストメソッド内で\n
    使用するためのセッションを返す
    """
    testdb.add_all(stock_prices_test_data_001)
    return testdb


class TestDelsert():
    """
    全DELETE全INSERT処理を実施するdelsert()メソッドのテストクラス
    """
    @pytest.mark.smoke
    def test_delsert_record_count(self, session_001):
        pass


class TestUpsert():
    """
    UPSERT処理を実施するupsert()メソッドのテストクラス
    """
    @pytest.mark.smoke
    def test_upsert_record_count(self, session_001):
        pass
