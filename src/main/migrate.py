# flake8: noqa
import os
import sys
import pathlib
import argparse
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import text

# src/mainフォルダパスを追加し、src/mainフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(str(pathlib.Path(__file__).resolve().parent))
from common.db.base_engine import BaseEngine  # noqa: #402
from common.logger.common_logger import CommonLogger  # noqa: #402
from stock.dto.stock_dto import Base, Company, StockPrice  # noqa: #402

logger = CommonLogger().get_application_logger(
    __name__,
)

def migrate_db(is_insert: str):
    # 認証情報は環境変数から取得する
    engine = BaseEngine(
        os.environ['POSTGRES_USER'],
        os.environ['POSTGRES_PASSWORD'],
        os.environ['POSTGRES_HOST'],
        os.environ['POSTGRES_PORT'],
        os.environ['POSTGRES_DB'],
    ).engine

    # DBに存在しない全てのテーブルを作成する
    # 作成済のテーブルについてはスキップする
    # ALTER TABLEについては、DTOの修正とSQLで対応する
    tables = [Company.__tablename__, StockPrice.__tablename__]
    logger.info('DB Migration start...')
    for tn in tables:
        try:
            Base.metadata.tables[tn].create(bind=engine, checkfirst=False)
            logger.info(f'{tn} table created.')
        except ProgrammingError:
            logger.info(f'{tn} table is already exist. '
                        f'Skip creating table.')

    logger.info('DB Migration end...')

    if is_insert == 'true':
        logger.info('Insert master data start...')
        insert_master_data(engine)
        logger.info('Insert master data end...')


def insert_master_data(
    engine
):
    """
    マスターデータを格納するテーブルについて、migrate.py実行時に全てのマスターデータをINSERTします(UPSERT)
    """
    with engine.connect() as con:
        # Companyテーブル
        columns = ('company_id', 'company_name', 'stock_code', 'country_code', 'listed_market', 'foundation_date', 'longitude', 'latitude')
        data = (
            ('0001', '株式会社テクノプロ ', '6028', 'JP', '東証1部', '1997-06-01', 35.66, 139.73),
            ('0002', '株式会社ALBERT', '3906', 'JP', '東証マザーズ', '2005-07-01', 35.70, 139.69),
            ('0003', '株式会社KDDI', '9433', 'JP', '東証1部', '1984-06-01', 35.70, 139.75),
            ('0004', '株式会社NTTドコモ', '9437', 'JP', '東証1部', '1992-07-01', 35.67, 139.74),
        )
        record_list = [dict(zip(columns, d)) for d in data]

        for record in record_list:
            con.execute(text("""
                             INSERT INTO Company
                             VALUES (:company_id, :company_name, :stock_code, :country_code,
                             :listed_market, :foundation_date, :longitude, :latitude)
                             ON CONFLICT DO NOTHING"""), **record)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--is_insert', default='false')
    args = parser.parse_args()
    migrate_db(args.is_insert)
