import datetime
import pandas as pd
import pandas_datareader.data as web


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
    ):
        """
        指定の銘柄コードに対して、pandas-datareaderを使ってデータを取得するためのクラス

        stooqデータソースから取得する株価データはStooqに存在する範囲で全てのデータを取得するようになっている\n
        （期間指定不可）ため、引数の開始日と終了日に従ってデータを絞り込む（デフォルトは絞り込み無し）

        Parameters
        ----------
        stock_code: str
            株価取得対象となる銘柄コード
        start_date: datetime.date
            株価データの取得開始日
        end_date: datetime.date
            株価データの取得終了日
        """
        stock_df = web.DataReader(stock_code, 'stooq')
        stock_df = stock_df[(stock_df.index >= pd.to_datetime(start_date)) &
                            (stock_df.index <= pd.to_datetime(end_date))]
        return stock_df
