import os
import sys
import pathlib
from typing import List
from sqlalchemy.orm import Session

# src/mainフォルダパスを追加し、src/mainフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent)))
from stock.dto.stock_dto import Company  # noqa: #402
from stock.main.stock_api import StooqAPI  # noqa: #402
from stock.main.stock_crawler import KabutanCrawler  # noqa: #402


class JpStockFactory(object):
    """
    日本の株式市場に上場している企業と、海外(US, Europe)のではそれぞれ株価データの取得先や
    取得方法が異なるので、ファクトリクラスが必要なインタフェース(クラス)群を生成する
    """
    def __init__(self):
        pass

    def get_target_stock_codes(
        self,
        session: Session
    ) -> List[str]:
        """
        Companyテーブルを参照し、国コード(country_code)が"JP"の企業の銘柄コード(stock_code)
        をリスト形式で返す

        Parameters
        ----------
        session: Session
            SQL AlchemyでDBを操作するためのSessionクラス

        Returns
        ----------
        stock_codes: List[str]
            取得対象となる銘柄コードのリスト
        """
        stock_codes_dtos = session.query(Company.stock_code).filter(
            Company.country_code == 'JP'
        ).all()
        stock_codes = [dto.stock_code for dto in stock_codes_dtos]
        return stock_codes

    def get_stock_api(self) -> StooqAPI:
        """
        pandas-datareaderによるデータ取得に使用するクラスを返す

        Returns
        ----------
        stock_api: StooqAPI
            pandas-datareaderにより、日本市場の株価データを取得するクラス
        """
        stock_api = StooqAPI()
        return stock_api

    def get_stock_crawler(self) -> KabutanCrawler:
        """
        Webクローリングによるデータ取得に使用するクラスを返す

        Returns
        ----------
        stock_api: KabutanCrawler
            https://kabutan.jpのクローリングにより、日本市場の株価データを取得するクラス
        """
        stock_crawler = KabutanCrawler()
        return stock_crawler
