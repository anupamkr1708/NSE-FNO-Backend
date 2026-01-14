# app/services/signal_deduplicator.py

from datetime import date
from sqlalchemy.orm import Session
from app.db import models

class SignalDeduplicator:
    """
    Ensures only ONE signal per (symbol, rule, date)
    """

    def __init__(self):
        self._seen = set()  # (symbol, rule, date)

    def is_duplicate(self, db: Session, symbol: str, rule: str, ts):
        key = (symbol, rule, ts.date())

        # 🔥 Fast in-memory check
        if key in self._seen:
            return True

        # 🔒 DB-level safety check
        exists = (
            db.query(models.Signal)
            .filter(
                models.Signal.symbol == symbol,
                models.Signal.rule == rule,
                models.Signal.time >= ts.date(),
                models.Signal.time < ts.date().replace(day=ts.day + 1)
            )
            .first()
        )

        if exists:
            self._seen.add(key)
            return True

        self._seen.add(key)
        return False
