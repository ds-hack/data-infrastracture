import datetime
import pandas as pd
import pandas_datareader.data as web
from typing import List
from logging import Logger


class StooqAPI(object):
    """
    pandas-datareaderのデータソースとしてStooqというポーランドのサイトからデータを取得する。

    get_stock_priceというインタフェースを実装し、将来的にデータソースが変わった際にStockManagerクラスに影響が及ばないようにする。
    """
    def __init__(self):
        pass

    def get_stock_price(
        self,
        stock_code: str,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        logger: Logger = None,
    ) -> List[pd.DataFrame]:
        """
        指定の銘柄コードに対して、pandas-datareaderを使ってデータを取得するためのクラス

        stooqデータソースから取得する株価データはStooqに存在する範囲で全てのデータを取得するようになっている
        （期間指定不可）ため、引数の開始日と終了日に従ってデータを絞り込む。デフォルトは絞り込み無し。
        現時点では日本企業のみを取得対象とすることを前提とし、海外企業は別のAPIを使用することとするため、
        stock_codeに".JP"を付与してリクエストする。

        Parameters
        ----------
        stock_code: str
            株価取得対象となる銘柄コード
        start_date: datetime.date
            株価データの取得開始日
        end_date: datetime.date
            株価データの取得終了日
        """
        stock_df = web.DataReader(stock_code + '.JP', 'stooq')
        try:
            # デフォルトとして開始日は2010-01-01, 終了日は本日の日付とする
            start_date = pd.to_datetime(start_date) if start_date\
                is not None else pd.to_datetime('2010-01-01')
            end_date = pd.to_datetime(end_date) if end_date\
                is not None else pd.to_datetime(datetime.datetime.now())
            stock_df = stock_df[
                (stock_df.index >= pd.to_datetime(start_date)) &
                (stock_df.index <= pd.to_datetime(end_date))
            ]
        except Exception as e:
            if logger is not None:
                logger.error(f'Failed get api {stock_code}: {e}')
            return None

        return stock_df
