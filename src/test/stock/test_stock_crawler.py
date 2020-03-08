import os
import sys
import pathlib
import pytest

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'main'))
from stock.main.stock_crawler import KabutanCrawler  # noqa: #402


class TestKabutanCrawler():
    """
    KabutanCrawlerクラスのユニットテスト

    クローリングの自動テストは相手サーバーの負荷とテスト速度の観点から最低限に絞る
    """
    @pytest.mark.smoke
    def test_get_stock_price(self, application_logger):
        """
        存在する銘柄コードを指定した際に、期待している全てのカラムを持つ株価データを
        取得できることをテスト
        """
        stock_crawler = KabutanCrawler()
        stock_df = stock_crawler.get_stock_price('6028',
                                                 application_logger)
        assert len(stock_df) == 1
        assert 'Open' in stock_df.columns
        assert 'High' in stock_df.columns
        assert 'Low' in stock_df.columns
        assert 'Close' in stock_df.columns
        assert 'Volume' in stock_df.columns

    @pytest.mark.smoke
    def test_get_stock_price_none(self, application_logger):
        """
        存在しない銘柄コードを指定した際に、Noneが返されることをテスト
        """
        stock_crawler = KabutanCrawler()
        stock_df = stock_crawler.get_stock_price('NotExistCode',
                                                 application_logger)
        assert stock_df is None
