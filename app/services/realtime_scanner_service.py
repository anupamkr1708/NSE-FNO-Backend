from datetime import date
from logzero import logger

from app.db.session import SessionLocal
from app.db import models
from app.services.signal_deduplicator import SignalDeduplicator


class RealTimeScannerService:
    """
    Runs scanner logic on every completed 5-minute candle (LIVE).
    Triggered by CandleBuilder.on_candle_close
    """

    def __init__(self, levels_service):
        self.levels = levels_service
        self.dedup = SignalDeduplicator()
        self.token_symbol_cache = {}

    # -------------------------------------------------
    def on_candle_close(self, candle: dict):
        """
        candle = {
            token, start, open, high, low, close, volume
        }
        """
        db = SessionLocal()
        try:
            token = candle["token"]
            ts = candle["start"]

            symbol = self._get_symbol(db, token)
            if not symbol:
                return

            lvl = self.levels.get_levels_for_today(db, symbol, ts.date())
            if not lvl:
                return

            signal = self.check_signal(symbol, candle, lvl)
            if not signal:
                return

            # 🔥 DEDUPLICATION
            if self.dedup.is_duplicate(db, symbol, signal.rule, ts):
                return

            db.add(signal)
            db.commit()

            logger.warning(
                f"🚨 LIVE SIGNAL → {symbol} | {signal.rule} | {signal.move_pct:.2f}%"
            )

        except Exception:
            db.rollback()
            logger.exception("Realtime scanner failed")

        finally:
            db.close()

    # -------------------------------------------------
    def _get_symbol(self, db, token: str):
        if token not in self.token_symbol_cache:
            inst = (
                db.query(models.Instrument)
                .filter(models.Instrument.token == token)
                .first()
            )
            if not inst:
                return None
            self.token_symbol_cache[token] = inst.symbol

        return self.token_symbol_cache[token]

    # -------------------------------------------------
    def check_signal(self, symbol, candle, lvl):
        o, c = candle["open"], candle["close"]
        move = (c - o) / o * 100

        pdh, pdl = lvl.pdh, lvl.pdl
        is_green = c > o
        is_red = c < o

        # 🔥 PDH Breakout
        if is_green and move > 3 and c > pdh:
            return models.Signal(
                symbol=symbol,
                time=candle["start"],
                rule="PDH_BREAKOUT",
                candle_index=0,
                move_pct=move,
            )

        # 🔥 PDL Breakdown
        if is_red and move < -3 and c < pdl:
            return models.Signal(
                symbol=symbol,
                time=candle["start"],
                rule="PDL_BREAKDOWN",
                candle_index=0,
                move_pct=move,
            )

        return None
