from typing import List
from sqlalchemy import func


class CommonDao(object):
    """
    スキーマに依存しないCRUD処理を行う

    条件(WHERE)の絡む処理は多様であり、クラスの責務が大きくなりすぎるのでサポートしない\n
    そのような処理は各アプリケーションのクラスに実装する\n
    具体的には下記の2つのDB更新処理を行うメソッドを持つ
    1. 元のレコードを全て削除し、与えられたDTOリストについて全て挿入する(全DEL全INS)
    2. 与えられたDTOリストに対して、主キーを元にテーブルに存在するか判定し、
       存在するレコードについてはUPDATE、存在しないレコードについてはINSERTを行う(UPSERT)
    """
    def __init__(
        self,
        session,
        dto_class,
        logger,
    ):
        """
        SQL AlchemyでDBを操作するためのセッション・DTOとアプリケーションログ出力用のロガーを受け取る

        Parameters
        ----------
        session: sqlalchemy.Session
            SQL AlchemyでDBを操作するためのSessionクラス
        dto_class: sqlalchemy.DeclarativeMeta
            処理対象テーブルのDTOクラス
        logger: logging.Logger
            アプリケーションログ出力用のロガー
        """
        self.session = session
        self.dto_class = dto_class
        self.logger = logger

    def delsert(
        self,
        dtos,
        primary_keys: List[str],
    ):
        """
        元のレコードを全て削除し、与えられたDTOリストについて全て挿入する

        Parameters
        ----------
        dtos: List[sqlalchemy.DeclarativeMeta]
            全DEL全INS対象のDTOリスト
        """
        # 削除レコード数と挿入レコード数をロギングする
        primary_key = f'self.dto_class.{primary_keys[0]}'
        old_count = \
            self.session.query(func.count(eval(primary_key))).scalar()
        # DELETE
        self.logger.info(f'Delete {old_count} records '
                         f'from {self.dto_class.__tablename__} table')
        self.session.query(self.dto_class).delete()
        # INSERT
        self.logger.info(f'Insert {len(dtos)} records '
                         f'into {self.dto_class.__tablename__} table')
        self.session.add_all(dtos)

    def upsert(
        self,
        dtos,
        primary_keys: List[str],
    ):
        """
        与えられたDTOリストに対して、主キーを元にテーブルに存在するか判定し、\n
        存在するレコードについてはUPDATE、存在しないレコードについてはINSERTを行う

        前提条件として、データベースの挿入日時を記録するins_tsカラムを持つことを想定し、\n
        UPDATE時にins_tsを書き換えないように配慮する

        Parameters
        ----------
        dtos: List[sqlalchemy.DeclarativeMeta]
            UPSERT対象のDTOリスト
        """
        upsert_dto_dict = {}  # 主キー(タプル)をキー、dtoをバリューとするディクショナリ
        for dto in dtos:
            p_keys = (eval(f'dto.{p_key}') for p_key in primary_keys)
            upsert_dto_dict[p_keys] = dto

        # 主キーが一致するdtoをsession.merge()によりUPDATEする
        # その際UPDATEレコードについては、ins_ts(挿入時のタイムスタンプ)は前レコード値を保持する必要がある
        for old_rec in self.session.query(self.dto_class).all():
            old_pkeys = (eval(f'old_rec.{p_key}') for p_key in primary_keys)
            if old_pkeys in upsert_dto_dict:
                update_dto = upsert_dto_dict.pop(old_pkeys)
                update_dto.ins_ts = old_rec.ins_ts
                self.session.merge(update_dto)
        self.logger.info(f'Updated {len(dtos) - len(upsert_dto_dict)} records '
                         f'on {self.dto_class.__tablename__} table')

        # 存在しないレコードのINSERT
        self.logger.info(f'Insert {len(upsert_dto_dict)} records '
                         f'into {self.dto_class.__tablename__} table')
        self.session.add_all(upsert_dto_dict.values())
