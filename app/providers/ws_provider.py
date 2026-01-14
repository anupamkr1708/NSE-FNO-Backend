import json
import struct
import websocket
from threading import Thread
from datetime import datetime
from logzero import logger

from app.config import settings
from app.providers.smartapi_provider import SmartAPIProvider
from app.db.session import SessionLocal
from app.db import models
from app.services.candle_builder import CandleBuilder
from app.services.realtime_scanner_service import RealTimeScannerService
from app.services.levels_service import LevelsService

WS_URL = "wss://smartapisocket.angelone.in/smart-stream"


class WebSocketProvider:
    def __init__(self, max_tokens=50):
        self.ws = None
        self.feed_token = None
        self.client_id = settings.SMARTAPI_CLIENT_ID
        self.api_key = settings.SMARTAPI_KEY
        self.max_tokens = max_tokens

        # ---- CORE SERVICES ----
        self.provider = SmartAPIProvider()
        self.levels = LevelsService(self.provider)
        self.scanner = RealTimeScannerService(self.levels)

        self.candle_builder = CandleBuilder(
            on_candle_close=self.scanner.on_candle_close
        )

        # ---- CACHE ----
        self.token_symbol_map = {}
        self.tokens = []

    # -------------------------------------------------
    def initialize(self):
        self.provider._ensure_login()
        self.feed_token = self.provider.client.feed_token
        logger.info("Feed Token Acquired")

        self.tokens = self._load_fno_stock_tokens()

    # -------------------------------------------------
    def _load_fno_stock_tokens(self):
        """
        Load ONLY F&O stocks mapped to NSE Cash (CM)
        """
        db = SessionLocal()

        # Step 1: F&O stock symbols
        fno_symbols = (
            db.query(models.Instrument.symbol)
            .filter(models.Instrument.exchange == "NFO")
            .filter(models.Instrument.segment == "FNO")
            .filter(models.Instrument.symbol.op("~")("^[A-Z]+$"))  # stock only
            .distinct()
            .all()
        )

        fno_symbols = [s[0] for s in fno_symbols]

        # Step 2: Map to NSE CM tokens
        cm_instruments = (
            db.query(models.Instrument)
            .filter(models.Instrument.exchange == "NSE")
            .filter(models.Instrument.symbol.in_(fno_symbols))
            .all()
        )

        db.close()

        # ---- CACHE TOKEN → SYMBOL ----
        for inst in cm_instruments:
            self.token_symbol_map[inst.token] = inst.symbol

        tokens = list(self.token_symbol_map.keys())

        # ---- FORCE LIQUID TEST TOKENS (SAFE) ----
        TEST_TOKENS = {
            "26009": "NIFTY",
            "26037": "BANKNIFTY",
            "2885": "RELIANCE",
            "1594": "INFY",
        }

        for t, s in TEST_TOKENS.items():
            self.token_symbol_map[t] = s
            tokens.insert(0, t)

        tokens = list(dict.fromkeys(tokens))[: self.max_tokens]

        logger.info(f"Loaded {len(tokens)} NSE CM tokens for WebSocket")
        return tokens

    # -------------------------------------------------
    def start(self):
        logger.info("Connecting to SmartAPI Neo WebSocket...")

        self.ws = websocket.WebSocketApp(
            WS_URL,
            header=[
                f"X-Client-Code:{self.client_id}",
                f"X-Feed-Token:{self.feed_token}",
                f"X-Api-Key:{self.api_key}",
            ],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        Thread(
            target=self.ws.run_forever,
            kwargs={"ping_interval": 20, "ping_timeout": 10},
            daemon=True,
        ).start()

    # -------------------------------------------------
    def subscribe(self):
        sub_msg = {
            "correlationID": "fno-live-feed",
            "action": 1,
            "params": {
                "mode": 1,  # LTP
                "tokenList": [
                    {
                        "exchangeType": 1,  # NSE
                        "tokens": self.tokens,
                    }
                ],
            },
        }

        logger.info(f"Subscribing to {len(self.tokens)} tokens")
        self.ws.send(json.dumps(sub_msg))

    # -------------------------------------------------
    def on_open(self, ws):
        logger.info("WebSocket Connected")
        self.subscribe()

    # -------------------------------------------------
    def on_message(self, ws, message):
        if isinstance(message, (bytes, bytearray)):
            self._handle_binary_tick(message)

    # -------------------------------------------------
    def _handle_binary_tick(self, raw: bytes):
        try:
            token = raw[2:27].decode("utf-8").rstrip("\x00")
            ltp = struct.unpack("<I", raw[27:31])[0] / 100
            volume = struct.unpack("<I", raw[31:35])[0]

            symbol = self.token_symbol_map.get(token)
            if not symbol:
                return

            self.candle_builder.update_tick(
                token=token,
                ltp=ltp,
                volume=volume,
                ts=datetime.now(),
            )

            logger.debug(f"TICK {symbol} ({token}) → {ltp}")

        except Exception:
            logger.exception("Binary tick parse failed")

    # -------------------------------------------------
    def on_error(self, ws, error):
        logger.error(f"WebSocket Error: {error}")

    def on_close(self, ws, *args):
        logger.warning("WebSocket Closed")
