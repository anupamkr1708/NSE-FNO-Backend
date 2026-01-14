from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/instruments", tags=["Instruments"])


@router.get("/fno")
def get_fno_stocks(db: Session = Depends(get_db)):
    """
    F&O stock universe (no options, no indices)
    """
    return (
        db.query(models.Instrument)
        .filter(models.Instrument.exchange == "NSE")
        .filter(models.Instrument.segment == "FNO")
        .filter(models.Instrument.symbol.notin_(
            ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
        ))
        .order_by(models.Instrument.symbol)
        .all()
    )
