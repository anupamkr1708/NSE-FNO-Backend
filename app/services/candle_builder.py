from datetime import datetime
from collections import defaultdict
from threading import Lock, Thread
import time
from typing import Optional, Dict, Any, List

from app.db.session import SessionLocal
from app.db import models
from logzero import logger


class CandleBuilder:
    """
    Builds 5-minute OHLC candles from incoming ticks.
    On candle close:
      - Stores to DB
      - Triggers realtime scanner callback
    """

    def __init__(self, bucket_minutes=5, on_candle_close=None):
        self.bucket_minutes = bucket_minutes
        self.on_candle_close = on_candle_close

        self.live: Dict[str, Dict[str, Any]] = {}
        self.locks: Dict[str, Lock] = defaultdict(Lock)

        self.completed_queue: List[Dict[str, Any]] = []
        self.queue_lock = Lock()

        self._stop = False
        Thread(target=self._periodic_flush, daemon=True).start()

    def _bucket_start(self, ts: datetime) -> datetime:
        minute = (ts.minute // self.bucket_minutes) * self.bucket_minutes
        return ts.replace(minute=minute, second=0, microsecond=0)

    def update_tick(
        self,
        token: str,
        ltp: float,
        volume: float,
        ts: Optional[datetime] = None,
    ):
        ts = ts or datetime.now()
        start = self._bucket_start(ts)

        with self.locks[token]:
            cur = self.live.get(token)

            # NEW candle
            if not cur:
                self.live[token] = {
                    "token": token,
                    "start": start,
                    "open": ltp,
                    "high": ltp,
                    "low": ltp,
                    "close": ltp,
                    "volume": volume or 0,
                }
                return None

            # CANDLE CLOSED
            if cur["start"] != start:
                completed = cur.copy()

                self.live[token] = {
                    "token": token,
                    "start": start,
                    "open": ltp,
                    "high": ltp,
                    "low": ltp,
                    "close": ltp,
                    "volume": volume or 0,
                }

                with self.queue_lock:
                    self.completed_queue.append(completed)

                if self.on_candle_close:
                    self.on_candle_close(completed)

                return completed

            # UPDATE LIVE
            cur["high"] = max(cur["high"], ltp)
            cur["low"] = min(cur["low"], ltp)
            cur["close"] = ltp
            cur["volume"] += volume or 0

            return None

    def _periodic_flush(self):
        while not self._stop:
            batch = []
            with self.queue_lock:
                if self.completed_queue:
                    batch = self.completed_queue[:]
                    self.completed_queue.clear()

            if batch:
                self._write_candles_to_db(batch)

            time.sleep(1)

    def _write_candles_to_db(self, candles):
        db = SessionLocal()
        try:
            for c in candles:
                inst = (
                    db.query(models.Instrument)
                    .filter(models.Instrument.token == c["token"])
                    .first()
                )
                if not inst:
                    continue

                db.add(
                    models.Candle5m(
                        symbol=inst.symbol,
                        start_time=c["start"],
                        open=c["open"],
                        high=c["high"],
                        low=c["low"],
                        close=c["close"],
                        volume=c["volume"],
                    )
                )

            db.commit()
            logger.info(f"🕯️ Stored {len(candles)} 5m candles")

        except Exception:
            db.rollback()
            logger.exception("Failed to store candles")
        finally:
            db.close()
