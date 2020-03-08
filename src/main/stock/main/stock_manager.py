import os
import sys
import pathlib
import datetime
import pandas as pd
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'main'))
from stock.dto.stock_dto import StockPrice  # noqa: #402


class StockManager(object):
    """
    pandas-datareaderを使って指定の銘柄コードに対する株価の情報を取得する。

    pandas-datareaderの最新のデータは翌立会日以降となるので、最新データについては木曜日までのデータしか存在しない。
    そこで最新金曜日の株価データについてのみ、別途Webクローリングによって取得する。

    StockManagerクラスはAPI経由で株価データを取得するためのStockAPIクラスと
    Webクローリングで株価データを取得するためのStockCrawlerクラスを保持する(集約)
    将来的にJP,US,EUなど扱う市場毎に異なるデータソースからデータを取得することになることも
    大いに考えられるため、クラスを切り出して集約することで変更の影響範囲を抑える設計としている。
    JP,US,EU等カテゴリ毎に異なるファミリ(クラスの集合）を必要とするためStockFactoryクラスから
    StockAPIクラスとStockCrawlerクラスを生成する実装とする。(AbstractFactory)

    Attributes
    ----------
    stock_api: object
        pandas-datareaderを使用して、API経由で株価データを取得するクラス
    stock_crawler: object
        Webクローリングを利用して、Web上からデータを取得するクラス
    """
    def __init__(
        self,
        session: Session,
        stock_api: object,
        stock_crawler: object
    ):
        """
        指定したStockAPIクラスとStockCrawlerクラスを使って株価データを取得する。

        インターフェース(抽象クラス)は定義せず、ダックタイピングを使用

        Parameters
        ----------
        session: Session
            SQL AlchemyでDBを操作するためのSessionクラス
        stock_api: object
            pandas-datareaderを使用して、API経由で株価データを取得するクラス
        stock_crawler: object
            Webクローリングを利用して、Web上からデータを取得するクラス
        """
        self.session = session
        self.stock_api = stock_api
        self.stock_crawler = stock_crawler

    def get_incremental_stock_price(
        self,
        stock_code: str,
        company_id: str,
    ) -> List[StockPrice]:
        """
        最新データが木曜日の場合のみ、クローリングによって金曜日のデータを取得する.

        APIを叩く処理、クローリング共に一定の時間がかかるため、必要最小限の処理を行う実装とする。

        Parameters
        ----------
        stock_code: str
            株価取得対象となる銘柄コード
        company_id: str
            株価取得対象となる企業ID

        Returns
        ----------
        stock_price_dtos: List[StockPrice]
            StockpriceテーブルのDtoのリスト
        """
        recent_date = self._get_recent_date(company_id) +\
            datetime.timedelta(days=1)
        # 最新データが金曜日且つ、直近2日間以内のデータの場合、処理しない(Noneを返す)
        if (recent_date is not None) and \
           (recent_date.weekday() == 4) and \
           ((datetime.date.today() - recent_date).days <= 2):
            return None
        # 最新データが木曜日且つ、直近3日間以内データの場合、クローリングで金曜日データを取得する
        elif (recent_date is not None) and \
             (recent_date.weekday() == 3) and \
             ((datetime.date.today() - recent_date).days < 7):
            stock_df = self.stock_crawler.get_stock_price(
                stock_code,
            )
        # 上記以外の場合、APIによりデータを取得する
        else:
            stock_df = self.stock_api.get_stock_price(
                stock_code,
                recent_date + datetime.timedelta(days=1),
            )
        if (stock_df is not None) and (len(stock_df) >= 1):
            # 取得したDataFrameにcompany_idのカラムを追加する
            stock_df['company_id'] = company_id
            stock_price_dtos = self._convert_stock_dtos(stock_df)
        return stock_price_dtos

    def _get_recent_date(
        self,
        company_id: str,
    ) -> datetime.date:
        """
        指定の銘柄コードについて、DBに保持している株価データの最新日を取得する。

        不要なクローリングを実施しないため、最新日からの増分のみをDBに保持する。

        Parameters
        ----------
        company_id: str
            株価取得対象となる企業ID

        Returns
        ----------
        recent_date: datetime.date
            最新の株価データ
        """
        res = self.session.\
            query(func.max(StockPrice.date).label('recent_date')).\
            filter(StockPrice.company_id == company_id).one()
        recent_date = res.recent_date if res else None
        return recent_date

    def _convert_stock_dtos(
        self,
        stock_df: pd.DataFrame
    ) -> List[StockPrice]:
        """
        pandasデータフレームの形式で保持している株価データをStockPriceクラス(DTOクラス)に変換する

        Parameters
        ----------
        stock_df: pd.DataFrame
            株価データを保持したデータフレーム

        Returns
        ----------
        stock_price_dtos: List[StockPrice]
            StockpriceテーブルのDtoのリスト
        """
        stock_df = stock_df.reset_index()
        stock_price_dtos = []

        for idx in stock_df.index:
            dto = StockPrice()
            dto.company_id = stock_df.at[idx, 'company_id']
            dto.date = stock_df.at[idx, 'Date'].date()
            dto.open_price = float(stock_df.at[idx, 'Open'])
            dto.high_price = float(stock_df.at[idx, 'High'])
            dto.low_price = float(stock_df.at[idx, 'Low'])
            dto.close_price = float(stock_df.at[idx, 'Close'])
            dto.volume = float(stock_df.at[idx, 'Volume'])
            stock_price_dtos.append(dto)

        return stock_price_dtos
