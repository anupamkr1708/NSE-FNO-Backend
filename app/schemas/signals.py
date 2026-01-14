from pydantic import BaseModel
from datetime import datetime

class SignalOut(BaseModel):
    id: int
    symbol: str
    time: datetime
    rule: str
    candle_index: int
    move_pct: float
    extra: str | None = None

    class Config:
        from_attributes = True
