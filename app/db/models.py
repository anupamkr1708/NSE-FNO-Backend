from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean
from app.db.session import Base

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    name = Column(String)
    exchange = Column(String)   # NFO
    segment = Column(String)    # FUT / OPT / FNO
    active = Column(Boolean, default=True)


class Candle5m(Base):
    __tablename__ = "candles_5m"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


class DailyLevel(Base):
    __tablename__ = "daily_levels"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    trade_date = Column(Date, index=True)
    pdh = Column(Float)
    pdl = Column(Float)
    pdc = Column(Float)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    time = Column(DateTime, index=True)
    rule = Column(String)
    candle_index = Column(Integer)
    move_pct = Column(Float)
    extra = Column(String, nullable=True)
