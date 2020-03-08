import os
import sys
import pathlib
import datetime
import pytest
import pandas as pd

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'main'))
from stock.dto.stock_dto import StockPrice  # noqa: #402
from stock.main.stock_manager import StockManager # noqa: #402
from stock.main.stock_api import StooqAPI  # noqa: #402
from stock.main.stock_crawler import KabutanCrawler  # noqa: #402


@pytest.fixture(scope='function', name='session_001')
def db_with_test_data_001(
    testdb,
    company_test_data_001,
    stock_prices_test_data_001
):
    """
    CommonDaoクラスのテストに使用するデータをDBに格納し、テストメソッド内で
    使用するためのセッションを返す
    """
    # テストメソッド実行毎にrollback()とadd_all()が実行される
    testdb.add_all(company_test_data_001)
    testdb.add_all(stock_prices_test_data_001)
    return testdb


class TestStockManager():
    """
    StockManagerクラスのユニットテスト
    """
    @pytest.mark.smoke
    def test_get_incremental_stock_price(
        self,
        session_001,
    ):
        """
        該当の企業IDによって下記の3パターンの処理が考えられる。

        1. 最新データが金曜日且つ、直近2日間以内のデータの場合、処理しない(Noneを返す)
        2. 最新データが木曜日且つ、直近3日間以内データの場合、クローリングで金曜日データを取得する
        3. 上記以外の場合、APIによりデータを取得する

        1. 2.は曜日によっては確認不可なので、自動テストには組み込めない。
        そのため、3.のパターンで株価データが取得できていることのみを確認し、株価の取得状況を
        ダッシュボード等でモニタリングすることで、対応する
        """
        stock_api = StooqAPI()
        stock_crawler = KabutanCrawler()
        stock_manager = StockManager(session_001, stock_api, stock_crawler)
        stock_price_dtos = stock_manager.get_incremental_stock_price(
            stock_code='6028',
            company_id='0001',
        )
        assert len(stock_price_dtos) >= 1

    @pytest.mark.parametrize('company_id, expected_date',
                             [('0001', datetime.date(2020, 2, 28)),
                              ('0002', datetime.date(2020, 2, 26)),
                              ('0004', None),
                              ])
    @pytest.mark.smoke
    def test_get_recent_date(
        self,
        session_001,
        company_id,
        expected_date,
    ):
        """
        各company_idについて、StockPriceテーブルに保持している株価データの最新日をテストする。

        StockManager初期化時に、StockAPIクラスとStockCrawlerクラスを指定する必要があるが、
        本テストには不要なため、Noneを与えて初期化する。
        """
        dummy_api = None
        dummy_crawler = None
        stock_manager = StockManager(session_001, dummy_api, dummy_crawler)
        recent_date = stock_manager._get_recent_date(company_id)

        if expected_date is None:
            assert recent_date is expected_date
        else:
            assert recent_date == expected_date

    @pytest.mark.smoke
    def test_convert_stock_dtos(
        self,
    ):
        """
        StockAPIクラスまたはStockCrawlerクラスから得たデータフレームをSQLAlchemyのDTOクラスに
        変換できていることを確認するテスト

        StockManager初期化時に、SessionクラスとStockAPIクラスとStockCrawlerクラスを指定する必要があるが、
        本テストには不要なため、Noneを与えて初期化する。
        """
        session = None
        dummy_api = None
        dummy_cralwer = None
        stock_manager = StockManager(session, dummy_api, dummy_cralwer)
        stock_data = [[pd.to_datetime('2020-03-08'), '1000.0', '2000.0',
                      '3000.0', '4000.0', '5000.0', '0001'],
                      [pd.to_datetime('2020-03-09'), '2000.0', '3000.0',
                      '4000.0', '5000.0', '6000.0', '0002']]
        col_names = ['Date', 'Open', 'High', 'Low',
                     'Close', 'Volume', 'company_id']
        stock_df = pd.DataFrame(stock_data, columns=col_names)

        stock_price_dtos = stock_manager._convert_stock_dtos(stock_df)
        assert len(stock_price_dtos) == 2
        assert stock_price_dtos[0].company_id == '0001'
        assert stock_price_dtos[0].date == datetime.date(2020, 3, 8)
        assert stock_price_dtos[0].open_price == 1000.0
        assert stock_price_dtos[0].high_price == 2000.0
        assert stock_price_dtos[1].low_price == 4000.0
        assert stock_price_dtos[1].close_price == 5000.0
        assert stock_price_dtos[1].volume == 6000.0
