import os
import sys
import pathlib
import pytest

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'main'))
from stock.main.stock_factory import JpStockFactory  # noqa: #402


@pytest.fixture(scope='function', name='session_001')
def db_with_test_data_001(
    testdb,
    company_test_data_001,
):
    """
    StockFactoryクラスのテストに使用するデータをDBに格納し、テストメソッド内で\n
    使用するためのセッションを返す
    """
    # テストメソッド実行毎にrollback()とadd_all()が実行される
    testdb.add_all(company_test_data_001)
    return testdb


class TestJpStockFactory():
    """
    JpStockFactoryクラスのユニットテスト
    """
    @pytest.mark.smoke
    def test_get_target_stock_codes(self, session_001):
        """
        Companyテーブルについて、country_codeが"JP"であるレコードを取得し、その銘柄コードのリストが\n
        正しく得られていることをテストする
        """
        stock_factory = JpStockFactory()
        stock_codes = stock_factory.get_target_stock_codes(session_001)
        assert type(stock_codes) == list
        assert len(stock_codes) == 4
        assert '2000' in stock_codes
