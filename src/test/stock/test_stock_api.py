import os
import sys
import pathlib
import datetime
import pytest

# src/mainフォルダパスを追加し、src/mainフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'main'))
from stock.main.stock_api import StooqAPI  # noqa: #402


class TestStooqAPI():
    """
    StooqAPIクラスのユニットテスト

    APIからデータを取得するテストは重いので、smokeテストの対象は絞る必要がある。
    """
    def test_get_stock_price_count(self):
        """
        tooqデータソースから取得する株価データはStooqに存在する範囲で全てのデータを取得するようになっている

        最新のデータは翌立会日以降となるので、週末は基本的に木曜日までのデータしか存在しない。
        """
        stock_api = StooqAPI()
        stock_df = stock_api.get_stock_price('6758',
                                             datetime.date(2020, 2, 24),
                                             None)
        # 2020/2/24は日曜日のため、2020/2/25〜2020/2/28 4件のデータが返される
        assert len(stock_df) == 4

    @pytest.mark.smoke
    def test_get_stock_price_check_columns(self):
        """
        APIより取得したデータが正しくカラムを保持しているか確認する。
        """
        stock_api = StooqAPI()
        stock_df = stock_api.get_stock_price('6758',
                                             datetime.date(2020, 2, 24),
                                             datetime.date(2020, 2, 28))
        assert 'Open' in stock_df.columns
        assert 'High' in stock_df.columns
        assert 'Low' in stock_df.columns
        assert 'Close' in stock_df.columns
        assert 'Volume' in stock_df.columns
