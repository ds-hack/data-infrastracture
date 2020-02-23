import os
import sys
import pathlib

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
from common.db.base_engine import BaseEngine  # noqa: #402
from common.logger.common_logger import CommonLogger  # noqa: #402
from stock.dto.stock_dto import Base, Company, StockPrice  # noqa: #402


if __name__ == '__main__':
    # 認証情報は環境変数から取得する (ref: forego run)
    engine = BaseEngine(
        os.environ['POSTGRESQL_USER'],
        os.environ['POSTGRESQL_PASSWORD'],
        os.environ['POSTGRESQL_HOST'],
        os.environ['POSTGRESQL_PORT'],
        os.environ['POSTGRESQL_DB_NAME'],
    ).engine

    sql_logger = CommonLogger().get_sql_logger(
        './log/stock/sql',
        'DEBUG',
    )

    # DBに存在しない全てのテーブルを作成する
    # ALTER TABLEについては、DTOの修正とSQLで対応する
    Base.metadata.create_all(bind=engine, checkfirst=False)
