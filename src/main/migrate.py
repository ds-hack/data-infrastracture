import os
import sys
import pathlib
from sqlalchemy.exc import ProgrammingError

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(str(pathlib.Path(__file__).resolve().parent))
from common.db.base_engine import BaseEngine  # noqa: #402
from common.logger.common_logger import CommonLogger  # noqa: #402
from stock.dto.stock_dto import Base, Company, StockPrice  # noqa: #402


if __name__ == '__main__':
    # 認証情報は環境変数から取得する
    engine = BaseEngine(
        os.environ['POSTGRES_USER'],
        os.environ['POSTGRES_PASSWORD'],
        os.environ['POSTGRES_HOST'],
        os.environ['POSTGRES_PORT'],
        os.environ['POSTGRES_DB'],
    ).engine

    # テスト用DBも併せて作成する
    test_engine = BaseEngine(
        os.environ['POSTGRES_TEST_USER'],
        os.environ['POSTGRES_TEST_PASSWORD'],
        os.environ['POSTGRES_TEST_HOST'],
        os.environ['POSTGRES_TEST_PORT'],
        os.environ['POSTGRES_TEST_DB'],
    ).engine

    logger = CommonLogger().get_application_logger(
        os.environ['APP_LOG_PATH'],
        __name__,
    )

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

        try:
            Base.metadata.tables[tn].create(
                bind=test_engine, checkfirst=False)
            logger.info(f'{tn} table created on testdb.')
        except ProgrammingError:
            logger.info(f'{tn} table is already exist in testdb. '
                        f'Skip creating table.')
    logger.info('DB Migration end...')
