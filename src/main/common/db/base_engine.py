from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Union


class BaseEngine(object):
    """
    SQL AlchemyでDBを操作するためのSessionクラスを構築する

    Attributes
    ----------
    engine: sqlalchemy.Engine
        SessionクラスがDB接続に使用するEngineクラス

    References
    ----------
    SQL Alchemy Documents(Engine):
        https://docs.sqlalchemy.org/en/13/core/engines.html
    SQL Alchemy Documents(Session Basics):
        https://docs.sqlalchemy.org/en/13/orm/session_basics.html
    """
    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: Union[int, str],
        db_name: str,
    ):
        """
        データベース接続情報を受け取り、create_engine()でEngineクラスを取得する

        Parameters
        ----------
        user: str
            接続ユーザー名
        password: str
            接続パスワード
        host: str
            DBのホスト
        port: Union[int, str]
            DBのポート番号
        db_name: str
            データベース名
        """
        conn_db = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
        self.engine = create_engine(conn_db, echo=False)

    def get_session(self):
        """
        SQL AlchemyでDBを操作するためのSessionクラスを取得する

        Returns
        ----------
        session: sqlalchemy.Session
            SQL AlchemyでDBを操作するためのSessionクラス
        """
        Session = sessionmaker(bind=self.engine)
        return Session()
