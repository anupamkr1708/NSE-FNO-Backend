from pydantic import BaseModel
from datetime import datetime

class Candle5mOut(BaseModel):
    symbol: str
    start_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    class Config:
        from_attributes = True
