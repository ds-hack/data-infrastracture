import os
import sys
import pathlib
from typing import List
from logging import Logger
from sqlalchemy import distinct
from sqlalchemy.orm import Session

# src/mainフォルダパスを追加し、src/mainフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent)))
from common.db.base_engine import BaseEngine  # noqa: #402
from common.db.common_dao import CommonDao  # noqa: #402
from common.logger.common_logger import CommonLogger  # noqa: #402
from stock.dto.stock_dto import Company, StockPrice, StockPriceMA  # noqa: #402
from stock.main.stock_manager import StockManager  # noqa: #402
from stock.main.stock_factory import JpStockFactory  # noqa: #402
from stock.main.ma_calculator import SMACalculator, EMACalculator, WMACalculator  # noqa: #402


class StockClient(object):
    """
    各種クラスを使用して、最新の株価データを取得しDB格納するクラス
    """
    def __init__(
        self,
        session: Session,
        logger: Logger,
    ):
        """
        SQL AlchemyでDBを操作するためのセッションとアプリケーションログ出力用のロガーを受け取る

        Parameters
        ----------
        session: sqlalchemy.Session
            SQL AlchemyでDBを操作するためのSessionクラス
        logger: logging.Logger
            アプリケーションログ出力用のロガー
        """
        self.session = session
        self.logger = logger

    def update_jp_stock_prices(self):
        """
        Companyテーブルに登録されている企業の中でcountry_codeが"JP"の企業について、
        StockManagerクラスにより株価データを取得し、DBにUPSERTで格納する。
        """
        self.logger.info('Start update_jp_stock_prices Job.')
        dao = CommonDao(session, StockPrice, logger)
        stock_factory = JpStockFactory()
        stock_codes = stock_factory.get_target_stock_codes(self.session)
        stock_manager = StockManager(
            self.session,
            stock_factory.get_stock_api(),
            stock_factory.get_stock_crawler(),
        )
        for stock_code in stock_codes:
            self.logger.info(f'Fetch StockCode:{stock_code} prices')
            company_id = self.get_company_id(stock_code, 'JP')
            stock_price_dtos = stock_manager.get_incremental_stock_price(
                stock_code,
                company_id,
            )
            # UPSERTによりDB更新
            if (stock_price_dtos is not None) and (len(stock_price_dtos) >= 1):
                dao.upsert(stock_price_dtos, ['company_id', 'date'])

    def calculate_ma(self):
        """
        stockpriceテーブルに登録されている全ての企業に対して、単純移動平均・指数平滑移動平均・加重移動平均
        の3通りの方法で日次の値を計算し、stockprice_maテーブルに格納する。

        暫定で短期(5日)・中期(25日)・長期(75日)の3パターンを計算するが、MACalculatorクラスのインタフェースとしては
        任意の日数で計算できるようにしておき、日数変更が用意なようにしておく。

        TODO: 一度全体を計算した後は最新日を計算するだけで十分なので、実行時間が長くなってきたら判定ロジックを追加する。
        """
        self.logger.info('Start calculate_ma Job.')
        dao = CommonDao(session, StockPriceMA, logger)
        ma_dtos = []
        company_ids = self.get_calc_companies()
        calculators = [
            SMACalculator(self.session, self.logger, company_ids),
            EMACalculator(self.session, self.logger, company_ids),
            WMACalculator(self.session, self.logger, company_ids),
        ]
        spans = [5, 25, 75]  # 計算期間

        for calculator in calculators:
            for span in spans:
                ma_dtos.extend(calculator.get_ma_values(span))
        # DELSERTにより更新(TODO対応後はUPSERTに変更)
        dao.delsert(ma_dtos, ['company_id', 'date', 'ma_type'])

    def get_company_id(
        self,
        stock_code: str,
        country_code: str,
    ):
        """
        Companyテーブルに対して、銘柄コードと国コードから企業コードを返す。

        Parameters
        ----------
        stock_code: str
            検索対象となる銘柄コード
        country_code: str
            検索対象となる国コード
        """
        company_id = self.session.query(Company.company_id).filter(
                        Company.stock_code == stock_code,
                        Company.country_code == "JP"
                     ).one().company_id
        return company_id

    def get_calc_companies(self) -> List[str]:
        """
        移動平均の計算対象企業を企業IDで取得する

        Returns
        ----------
        company_ids: List[str]
            移動平均の計算対象企業IDのリスト
        """
        result = self.session.query(
            distinct(StockPrice.company_id).label('company_id')).all()
        company_ids = [res.company_id for res in result]
        return company_ids


if __name__ == '__main__':
    session = BaseEngine(
        os.environ['POSTGRES_USER'],
        os.environ['POSTGRES_PASSWORD'],
        os.environ['POSTGRES_HOST'],
        os.environ['POSTGRES_PORT'],
        os.environ['POSTGRES_DB'],
    ).get_session()

    logger = CommonLogger().get_application_logger(
        __name__,
    )

    stock_client = StockClient(session, logger)
    stock_client.update_jp_stock_prices()
    stock_client.calculate_ma()

    session.commit()
