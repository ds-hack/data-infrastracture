from sqlalchemy import Column, String, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    """
    CompanyテーブルのDto
    """
    __tablename__ = 'company'
    __table_args__ = {
        'comment': '企業の主要な情報をマスタとして格納する\n'
                   '資本金・従業員数等の情報は時系列データなので、別テーブルで扱う'
    }

    company_id = Column(String(16), primary_key=True,
                        comment='システム内で設定する企業毎に一意となるコード')
    company_name = Column(String(256), nullable=False, comment='企業名')
    stock_code = Column(String(16), nullable=False, comment='銘柄コード')
    listed_market = Column(String(32), nullable=False, comment='上場市場')
    foundation_date = Column(DateTime, comment='設立日(月)')
    longitude = Column(Float, comment='本社所在地(経度)')
    latitude = Column(Float, comment='本社所在地(緯度)')

    # 外部キー制約
    company = relationship('StockPrice')


class StockPrice(Base):
    """
    StockPriceテーブルのDto
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
