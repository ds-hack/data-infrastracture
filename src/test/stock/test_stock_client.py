import os
import sys
import pathlib
import pytest

# src/mainフォルダパスを追加し、src/mainフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'main'))
from stock.main.stock_client import StockClient  # noqa: #402


@pytest.fixture(scope='function', name='session_001')
def db_with_test_data_001(
    testdb,
    company_test_data_001,
):
    """
    StockFactoryクラスのテストに使用するデータをDBに格納し、テストメソッド内で
    使用するためのセッションを返す
    """
    # テストメソッド実行毎にrollback()とadd_all()が実行される
    testdb.add_all(company_test_data_001)
    return testdb


class TestStockClient():
    """
    StockManagerを利用し、株価データをDBに格納するStockClientクラスのユニットテストを行うクラス
    """
    @pytest.mark.parametrize('company_id, stock_code, country_code',
                             [('0001', '2000', 'JP'),
                              ('0002', '3000', 'JP'),
                              ('0004', '5000', 'JP'),
                              ])
    @pytest.mark.smoke
    def test_get_company_id(
        self,
        session_001,
        company_id,
        stock_code,
        country_code,
    ):
        """
        銘柄コードと国コードから、正しく企業IDが取得できることをテスト
        """
        stock_client = StockClient(session_001, None)
        company_id_res = stock_client.get_company_id(stock_code, country_code)
        assert company_id == company_id_res
