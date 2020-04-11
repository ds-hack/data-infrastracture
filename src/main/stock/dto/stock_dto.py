from sqlalchemy import Column, String, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Company(Base):
    """
    companyテーブルのDto
    """
    __tablename__ = 'company'
    __table_args__ = {
        'comment': '企業の主要な情報をマスタとして格納する.日本の上場企業のみを対象.\n'
                   '資本金・従業員数等の情報は時系列データなので、別テーブルで扱う'
    }

    company_id = Column(String(16), primary_key=True,
                        comment='システム内で設定する企業毎に一意となるコード')
    company_name = Column(String(256), nullable=False, comment='企業名')
    stock_code = Column(String(16), nullable=False, comment='銘柄コード')
    country_code = Column(String(16), nullable=False, comment='国コード')
    listed_market = Column(String(32), nullable=False, comment='上場市場')
    foundation_date = Column(DateTime, comment='設立日(月)')
    longitude = Column(Float, comment='本社所在地(経度)')
    latitude = Column(Float, comment='本社所在地(緯度)')
    ins_ts = Column(DateTime, server_default=func.now())
    upd_ts = Column(DateTime, server_default=func.now())

    # 外部キー制約 (one-to-many)
    stockprices = relationship('StockPrice')
    stockprices_ma = relationship('StockPriceMA')


class StockPrice(Base):
    """
    stockpriceテーブルのDto
    """
    __tablename__ = 'stockprice'
    __table_args__ = {
        'comment': '企業毎の日毎の株価(始値・高値・安値・終値)・出来高を格納する'
    }

    company_id = Column(String(16), ForeignKey('company.company_id'),
                        primary_key=True,
                        comment='システム内で設定する企業毎に一意となるコード')
    date = Column(Date, primary_key=True, comment='日付')
    open_price = Column(Float, comment='株価(始値)')
    high_price = Column(Float, comment='株価(高値)')
    low_price = Column(Float, comment='株価(安値)')
    close_price = Column(Float, comment='株価(終値)')
    volume = Column(Float, comment='出来高')
    ins_ts = Column(DateTime, server_default=func.now())
    upd_ts = Column(DateTime, server_default=func.now())


class StockPriceMA(Base):
    """
    stockprice_maテーブルのDto
    """
    __tablename__ = 'stockprice_ma'
    __table_args__ = {
        'comment': '企業毎の日次の移動平均株価(SMA・EMA・WMA)を格納する'
    }

    company_id = Column(String(16), ForeignKey('company.company_id'),
                        primary_key=True,
                        comment='システム内で設定する企業毎に一意となるコード')
    date = Column(Date, primary_key=True, comment='日付')
    ma_type = Column(String(16), primary_key=True,
                     comment='移動平均の計算条件(ex. sma5, ema25, ...)')
    ma_value = Column('ma_value', Float, comment='ma_typeの条件下の移動平均株価')
    ins_ts = Column(DateTime, server_default=func.now())
    upd_ts = Column(DateTime, server_default=func.now())
