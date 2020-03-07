import os
import sys
import pathlib
import pytest
import datetime
from sqlalchemy import func

# srcフォルダパスを追加し、srcフォルダ起点でインポートする(#402 Lint Error抑制と合わせて使用)
sys.path.append(os.path.join(
    str(pathlib.Path(__file__).resolve().parent.parent.parent), 'main'))
from common.db.common_dao import CommonDao  # noqa: #402
from stock.dto.stock_dto import StockPrice  # noqa: #402


@pytest.fixture(scope='function', name='session_001')
def db_with_test_data_001(
    testdb,
    company_test_data_001,
    stock_prices_test_data_001
):
    """
    CommonDaoクラスのテストに使用するデータをDBに格納し、テストメソッド内で\n
    使用するためのセッションを返す
    """
    # テストメソッド実行毎にrollback()とadd_all()が実行される
    testdb.add_all(company_test_data_001)
    testdb.add_all(stock_prices_test_data_001)
    return testdb


class TestDelsert():
    """
    全DELETE全INSERT処理を実施するdelsert()メソッドのテストクラス
    """
    @pytest.mark.smoke
    def test_delsert_record_count(
        self,
        session_001,
        test_common_dao_delsert_data,
        application_logger,
    ):
        """
        全DELETE全INSERT処理を実施した後のレコード数が、想定通りであるか
        """
        stock_price_dao = CommonDao(session_001, StockPrice,
                                    application_logger)
        stock_price_dao.delsert(test_common_dao_delsert_data,
                                ['company_id', 'date'])
        record_count = session_001.query(
            func.count(StockPrice.company_id)).scalar()

        assert len(test_common_dao_delsert_data) == record_count

    @pytest.mark.parametrize('company_id, date',
                             [('0001JP', datetime.date(2020, 2, 24)),
                              ('0002JP', datetime.date(2020, 2, 25)),
                              ('0004JP', datetime.date(2020, 2, 29)),
                              ])
    @pytest.mark.smoke
    def test_delsert_is_correct_data(
        self,
        session_001,
        test_common_dao_delsert_data,
        application_logger,
        company_id,
        date,
    ):
        """
        全DELETE全INSERT処理を実施した後のレコードが、正しくDBに保持されているか

        delsertメソッド内ではdtoに手を加えていないので保持されていることのみを確認する
        """
        stock_price_dao = CommonDao(session_001, StockPrice,
                                    application_logger)
        stock_price_dao.delsert(test_common_dao_delsert_data,
                                ['company_id', 'date'])

        record = \
            session_001.query(
                StockPrice
            ).filter(
                StockPrice.company_id == company_id,
                StockPrice.date == date,
            ).first()

        assert record is not None


class TestUpsert():
    """
    UPSERT処理を実施するupsert()メソッドのテストクラス
    """
    @pytest.mark.smoke
    def test_upsert_record_count(
        self,
        session_001,
        test_common_dao_upsert_data,
        application_logger,
    ):
        """
        UPSERT処理を実施した後のレコード数が、想定通りであるか
        """
        stock_price_dao = CommonDao(session_001, StockPrice,
                                    application_logger)
        stock_price_dao.upsert(test_common_dao_upsert_data,
                               ['company_id', 'date'])
        record_count = session_001.query(
            func.count(StockPrice.company_id)).scalar()

        assert len(test_common_dao_upsert_data) == record_count

    @pytest.mark.parametrize('company_id, date',
                             [('0001JP', datetime.date(2020, 2, 29)),
                              ('0004JP', datetime.date(2020, 2, 29)),
                              ])
    @pytest.mark.smoke
    def test_upsert_is_correct_insert_data(
        self,
        session_001,
        test_common_dao_upsert_data,
        application_logger,
        company_id,
        date
    ):
        """
        UPSERT処理を実施した後のINSERT対象のレコードが、正しくDBに保持されているか

        upsertメソッド内ではdtoに手を加えていないので保持されていることのみを確認する
        """
        stock_price_dao = CommonDao(session_001, StockPrice,
                                    application_logger)
        stock_price_dao.upsert(test_common_dao_upsert_data,
                               ['company_id', 'date'])

        record = \
            session_001.query(
                StockPrice
            ).filter(
                StockPrice.company_id == company_id,
                StockPrice.date == date,
            ).first()

        assert record is not None

    @pytest.mark.parametrize('company_id, date',
                             [('0001JP', datetime.date(2020, 2, 24)),
                              ('0002JP', datetime.date(2020, 2, 25)),
                              ('0003JP', datetime.date(2020, 2, 25)),
                              ])
    @pytest.mark.smoke
    def test_upsert_is_correct_update_data(
        self,
        session_001,
        test_common_dao_upsert_data,
        application_logger,
        company_id,
        date,
    ):
        """
        UPSERT処理を実施した後のUPDATE対象のレコードが、正しくDBに保持されているか

        「ins_tsを書き換えていないこと」という観点が加わる
        """
        old_record = \
            session_001.query(
                StockPrice
            ).filter(
                StockPrice.company_id == company_id,
                StockPrice.date == date,
            ).first()

        stock_price_dao = CommonDao(session_001, StockPrice,
                                    application_logger)
        stock_price_dao.upsert(test_common_dao_upsert_data,
                               ['company_id', 'date'])

        record = \
            session_001.query(
                StockPrice
            ).filter(
                StockPrice.company_id == company_id,
                StockPrice.date == date,
            ).first()

        assert record is not None
        assert old_record.ins_ts == record.ins_ts
