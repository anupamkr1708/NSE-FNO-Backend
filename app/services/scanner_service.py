import asyncio
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from logzero import logger

from app.db import models
from app.services.universe_service import UniverseService
from app.routers.ws import manager


class ScannerService:
    def __init__(self, provider, levels_service,
                 threshold=3.0, proximity=0.3):
        self.provider = provider
        self.levels = levels_service
        self.threshold = threshold
        self.proximity = proximity / 100
        self.universe = UniverseService()
        self._latest = []

    @property
    def latest_signals(self):
        return self._latest

    async def run_intraday_loop(self, db_factory):
        logger.info("📡 Scanner loop started (F&O | WebSocket enabled)")
        while True:
            now = datetime.now().time()

            if time(9, 15) <= now <= time(15, 30):
                db = db_factory()
                await self.scan_once(db)
                db.close()

            await asyncio.sleep(60)

    async def scan_once(self, db: Session):
        today = getattr(self, "_force_date", date.today())
        instruments = self.universe.get_fno_universe(db)

        signals = []

        for inst in instruments:
            lvl = self.levels.ensure_daily_levels(
                db, inst.symbol, inst.token, today
            )
            if not lvl:
                continue

            c1, c2 = await self.first_two_candles(inst, today)

            for idx, candle in enumerate([c1, c2], start=1):
                if candle:
                    signal = self.check_signal(inst.symbol, candle, lvl, idx)
                    if signal:
                        signals.append(signal)

        if signals:
            for s in signals:
                db.add(s)
            db.commit()

            self._latest = signals
            logger.info(f"🚨 {len(signals)} signals generated")

            # 🔥 REAL-TIME BROADCAST
            for s in signals:
                await manager.broadcast({
                    "type": "signal",
                    "payload": {
                        "symbol": s.symbol,
                        "rule": s.rule,
                        "time": s.time.isoformat(),
                        "move_pct": s.move_pct
                    }
                })

    async def first_two_candles(self, inst, today):
        start = datetime(today.year, today.month, today.day, 9, 15)
        end   = datetime(today.year, today.month, today.day, 9, 25)

        raw = self.provider.get_5m_candles(
            "NSE", inst.token, start, end
        )

        if not raw:
            return None, None

        def parse(c):
            ts = c[0].split("+")[0]
            return {
                "timestamp": datetime.fromisoformat(ts),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
            }

        return (
            parse(raw[0]) if len(raw) > 0 else None,
            parse(raw[1]) if len(raw) > 1 else None,
        )

    def check_signal(self, symbol, candle, lvl, idx):
        o, c = candle["open"], candle["close"]
        move = (c - o) / o * 100

        pdh, pdl = lvl.pdh, lvl.pdl
        near = lambda p, l: abs(p - l) / l <= self.proximity

        is_green = c > o
        is_red = c < o

        if is_red and abs(move) <= self.threshold and near(c, pdh):
            return models.Signal(
                symbol=symbol,
                time=candle["timestamp"],
                rule="PDH_REJECTION",
                candle_index=idx,
                move_pct=move
            )

        if is_green and abs(move) <= self.threshold and near(c, pdl):
            return models.Signal(
                symbol=symbol,
                time=candle["timestamp"],
                rule="PDL_REJECTION",
                candle_index=idx,
                move_pct=move
            )

        if is_green and move > self.threshold and c > pdh:
            return models.Signal(
                symbol=symbol,
                time=candle["timestamp"],
                rule="PDH_BREAKOUT",
                candle_index=idx,
                move_pct=move
            )

        if is_red and move < -self.threshold and c < pdl:
            return models.Signal(
                symbol=symbol,
                time=candle["timestamp"],
                rule="PDL_BREAKDOWN",
                candle_index=idx,
                move_pct=move
            )

        return None
