from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db)):
    signals = (
        db.query(models.Signal)
        .order_by(models.Signal.time.desc())
        .limit(20)
        .all()
    )

    return {
        "signals": [
            {
                "symbol": s.symbol,
                "rule": s.rule,
                "time": s.time,
                "move_pct": s.move_pct,
            }
            for s in signals
        ]
    }
