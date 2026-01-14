from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import models
from app.providers.smartapi_provider import SmartAPIProvider

class LevelsService:
    def __init__(self, provider: SmartAPIProvider):
        self.provider = provider

    def ensure_daily_levels(self, db: Session, symbol: str, token: str, date_):
        existing = (
            db.query(models.DailyLevel)
            .filter_by(symbol=symbol, trade_date=date_)
            .first()
        )

        if existing:
            return existing

        prev_date = date_ - timedelta(days=1)
        start = datetime(prev_date.year, prev_date.month, prev_date.day, 9, 15)
        end = datetime(prev_date.year, prev_date.month, prev_date.day, 15, 30)

        raw = self.provider.get_5m_candles("NSE", token, start, end)
        if not raw:
            return None

        highs = [r[2] for r in raw]
        lows  = [r[3] for r in raw]
        closes = [r[4] for r in raw]

        lvl = models.DailyLevel(
            symbol=symbol,
            trade_date=date_,
            pdh=max(highs),
            pdl=min(lows),
            pdc=closes[-1],
        )

        db.add(lvl)
        db.commit()
        db.refresh(lvl)
        return lvl
