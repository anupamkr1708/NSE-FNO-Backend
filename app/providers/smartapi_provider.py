from SmartApi import SmartConnect
import pyotp
from datetime import datetime
from logzero import logger
from app.config import settings

class SmartAPIProvider:
    def __init__(self):
        self.api_key = settings.smartapi_key
        self.client_id = settings.smartapi_client_id
        self.pin = settings.smartapi_pin
        self.totp_secret = settings.smartapi_totp_secret
        self.client = None

    def _ensure_login(self):
        if self.client:
            return self.client

        client = SmartConnect(self.api_key)
        totp = pyotp.TOTP(self.totp_secret).now()
        data = client.generateSession(self.client_id, self.pin, totp)

        if not data.get("status"):
            raise Exception("SmartAPI Login Failed!")

        logger.info("SmartAPI Login Successful")
        self.client = client
        return client

    def get_5m_candles(self, exchange, token, from_dt, to_dt):
        client = self._ensure_login()

        params = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": "FIVE_MINUTE",
            "fromdate": from_dt.strftime("%Y-%m-%d %H:%M"),
            "todate": to_dt.strftime("%Y-%m-%d %H:%M"),
        }

        resp = client.getCandleData(params)

        if resp.get("status"):
            return resp["data"]

        logger.error(f"Candle fetch failed: {resp}")
        return []
