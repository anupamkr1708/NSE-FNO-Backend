# app/routers/signals.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models

print("✅ signals router loaded")

router = APIRouter(
    prefix="/signals",
    tags=["Signals"]
)


@router.get("/", summary="All signals")
def get_signals(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Signal)
        .order_by(models.Signal.time.desc())
        .limit(limit)
        .all()
    )


@router.get("/latest", summary="Latest signals (dashboard)")
def latest_signals(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(models.Signal)
        .order_by(models.Signal.time.desc())
        .limit(limit)
        .all()
    )

    return {
        "signals": [
            {
                "symbol": r.symbol,
                "rule": r.rule,
                "time": r.time.isoformat(),
                "move_pct": r.move_pct,
            }
            for r in rows
        ]
    }
