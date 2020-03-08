import time
import requests
import pandas as pd
from logging import Logger
from typing import List
from bs4 import BeautifulSoup


class KabutanCrawler(object):
    """
    Webクローリングのデータソースとしてhttps://kabutan.jp/のサイトからデータを取得する。

    get_stock_priceというインタフェースを実装し、将来的にデータソースが変わった際にStockManagerクラスに影響が及ばないようにする。
    """
    def __init__(self):
        pass

    def get_stock_price(
        self,
        stock_code: str,
        logger: Logger = None,
    ) -> List[pd.DataFrame]:
        """
        指定の銘柄コードに対して、BeautifulSoupを使ってデータを取得するためのクラス

        start_dateが現在の日付と一致している場合、クローリングを実施しない。

        Parameters
        ----------
        stock_code: str
            株価取得対象となる銘柄コード
        logger: logging.Logger
            アプリケーションで使用するロガー
        """
        # クローリングの間隔を最低1secは空ける
        time.sleep(1)
        base_url = f'https://kabutan.jp/stock/kabuka?code={stock_code}'
        try:
            response = requests.get(base_url)
            bs = BeautifulSoup(response.text, 'html.parser')
            stock_data = {}
            # stock_kabuka0テーブルのth要素は日付、td要素は始値、高値、安値、終値、前日比、前日比%、売買高の順に並ぶ
            stock_table = bs.find('table', class_='stock_kabuka0')
            stock_data['Date'] = pd.to_datetime(
                stock_table.find('tbody').find('th').time['datetime'])

            columns = ['Open', 'High', 'Low', 'Close', None, None, 'Volume']
            for col_name, data in zip(columns,
                                      stock_table.find('tbody').
                                      find_all(['td'])):
                if col_name:
                    stock_data[col_name] = data.get_text().replace(',', '')
            stock_df = pd.DataFrame([stock_data]).set_index('Date')
        except Exception as e:
            if logger is not None:
                logger.error(f'Cannot crawl {stock_code}: {e}')
            return None

        return stock_df
