from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/candles")
def get_candles(
    symbol: str = Query(...),
    limit: int = Query(100),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Candle5m)
        .filter(models.Candle5m.symbol == symbol)
        .order_by(models.Candle5m.start_time.desc())
        .limit(limit)
        .all()
    )
