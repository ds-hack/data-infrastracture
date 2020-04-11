import os
import sys
import pathlib
import datetime
from typing import List
from logging import Logger
from sqlalchemy import Float, and_, case
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import literal_column

# src/mainフォルダパスを追加し、src/mainフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent)))
from stock.dto.stock_dto import StockPrice, StockPriceMA  # noqa: #402


class SMACalculator(object):
    """
    stockpriceテーブルの株価データをもとに単純移動平均(SMA)を計算する

    get_ma_values()を実装する
    """
    def __init__(
        self,
        session: Session,
        logger: Logger,
        company_ids: List[str],
    ):
        self.session = session
        self.logger = logger
        self.company_ids = company_ids

    def get_ma_values(
        self,
        span: int,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> List[StockPriceMA]:
        """
        指定期間・指定日数について、単純移動平均(SMA)を計算する
        現時点ではspanのみを考慮し、全期間について単純移動平均(SMA)を計算する

        Parameters
        ----------
        span: int
            移動平均の計算日数(X日移動平均)
        start_date: datetime.date
            移動平均の計算期間開始日
        end_date: datetime.date
            移動平均の計算期間終了日

        Returns
        ----------
        sma_dtos: List[StockPriceMA]
            stockprice_MAテーブルのDtoのリスト
        """
        sma_dtos = []
        # ウィンドウ関数によりspan-1日前までの平均を各日付について取得する
        sma_results = self.session.query(
            StockPrice.company_id,
            StockPrice.date,
            func.avg(StockPrice.close_price).over(
                partition_by=StockPrice.company_id,
                order_by=StockPrice.date,
                rows=(-(span - 1), 0),
            ).label('sma'),
            func.count(StockPrice.close_price).over(
                partition_by=StockPrice.company_id,
                order_by=StockPrice.date,
                rows=(-(span - 1), 0),
            ).label('count'),
        ).order_by(
            StockPrice.company_id,
            StockPrice.date
        ).all()

        for res in sma_results:
            if res.count >= span:
                dto = StockPriceMA()
                dto.company_id = res.company_id
                dto.date = res.date
                dto.ma_type = f'sma{span}'
                dto.ma_value = res.sma
                sma_dtos.append(dto)

        return sma_dtos


class EMACalculator(object):
    """
    stockpriceテーブルの株価データをもとに指数平滑移動平均(EMA)を計算する

    get_ma_values()を実装する
    """
    def __init__(
        self,
        session: Session,
        logger: Logger,
        company_ids: List[str],
    ):
        self.session = session
        self.logger = logger
        self.company_ids = company_ids

    def get_ma_values(
        self,
        span: int,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> List[StockPriceMA]:
        """
        指定期間・指定日数について、指数平滑移動平均(EMA)を計算する

        Parameters
        ----------
        span: int
            移動平均の計算日数(X日移動平均)
        start_date: datetime.date
            移動平均の計算期間開始日
        end_date: datetime.date
            移動平均の計算期間終了日

        Returns
        ----------
        ema_dtos: List[StockPriceMA]
            stockprice_MAテーブルのDtoのリスト
        """
        ema_dtos = []
        alpha = 2 / (1 + span)  # 平滑化定数
        # WITH RECURSIVEにより再帰的に指数平滑移動平均を計算
        stockprice = self.session.query(
            StockPrice.company_id,
            StockPrice.date,
            literal_column(str(alpha), type_=Float).label('alpha'),
            func.row_number().over(
                partition_by=StockPrice.company_id,
                order_by=StockPrice.date,
            ).label('row_number'),
            StockPrice.close_price,
        ).cte(name='all')

        # 非再起項(1日(行)目からスタート)
        ema = self.session.query(
            stockprice,
            stockprice.c.close_price.label('ema'),
        ).filter(
            stockprice.c.row_number == 1,
        ).cte(recursive=True, name='ema')

        lalias = aliased(ema, name="l")
        ralias = aliased(stockprice, name="r")
        ema = ema.union_all(
            # 再起項(1日ずつJOINして再帰的にEMAを計算)
            self.session.query(
                ralias.c.company_id,
                ralias.c.date,
                ralias.c.alpha,
                ralias.c.row_number,
                ralias.c.close_price,
                (ralias.c.alpha * ralias.c.close_price +
                 (1 - ralias.c.alpha) * lalias.c.close_price).label('ema')
            ).join(lalias, and_(
                lalias.c.company_id == ralias.c.company_id,
                lalias.c.row_number == ralias.c.row_number - 1)
            )
        )
        ema_results = self.session.query(ema).all()

        for res in ema_results:
            if res.row_number >= span:
                dto = StockPriceMA()
                dto.company_id = res.company_id
                dto.date = res.date
                dto.ma_type = f'ema{span}'
                dto.ma_value = res.ema
                ema_dtos.append(dto)

        return ema_dtos


class WMACalculator(object):
    """
    stockpriceテーブルの株価データをもとに加重移動平均(WMA)を計算する

    get_ma_values()を実装する
    """
    def __init__(
        self,
        session: Session,
        logger: Logger,
        company_ids: List[str],
    ):
        self.session = session
        self.logger = logger
        self.company_ids = company_ids

    def get_ma_values(
        self,
        span: int,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> List[StockPriceMA]:
        """
        指定期間・指定日数について、加重移動平均(WMA)を計算する

        Parameters
        ----------
        span: int
            移動平均の計算日数(X日移動平均)
        start_date: datetime.date
            移動平均の計算期間開始日
        end_date: datetime.date
            移動平均の計算期間終了日

        Returns
        ----------
        wma_dtos: List[StockPriceMA]
            stockprice_MAテーブルのDtoのリスト
        """
        wma_dtos = []
        denominator = sum(range(span + 1))  # 重みの分母となる数
        stockprice = self.session.query(
            StockPrice.company_id,
            StockPrice.date,
            StockPrice.close_price,
            func.row_number().over(
                partition_by=StockPrice.company_id,
                order_by=StockPrice.date,
            ).label('row_number'),
        ).cte(name='all')

        # 自己結合と集約の組み合わせにより、指定のspanの重み付き和(加重移動平均)を計算する
        lalias = aliased(stockprice, name="l")
        ralias = aliased(stockprice, name="r")
        case_statement = case([
            ((lalias.c.row_number - ralias.c.row_number) == day,
             ralias.c.close_price * (span - day) / denominator)
            for day in range(span)
        ])

        wma_results = self.session.query(
            lalias.c.company_id,
            lalias.c.date,
            func.sum(case_statement).label('wma')
        ).join(ralias, and_(
            lalias.c.company_id == ralias.c.company_id,
            lalias.c.row_number - (span - 1) <= ralias.c.row_number,
            ralias.c.row_number <= lalias.c.row_number
        )).group_by(
            lalias.c.company_id,
            lalias.c.date,
        ).having(
            func.count() == span,
        ).order_by(
            lalias.c.company_id,
            lalias.c.date,
        ).all()

        for res in wma_results:
            dto = StockPriceMA()
            dto.company_id = res.company_id
            dto.date = res.date
            dto.ma_type = f'wma{span}'
            dto.ma_value = res.wma
            wma_dtos.append(dto)

        return wma_dtos
