from sqlalchemy.orm import Session
from app.db.models import Instrument

class UniverseService:
    """
    Production universe:
    - Select F&O eligible stocks
    - Map them to NSE CM instruments (price source)
    """

    EXCLUDE = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"}

    def get_fno_universe(self, db: Session):
        # Step 1: distinct F&O symbols
        fno_symbols = (
            db.query(Instrument.symbol)
            .filter(Instrument.segment == "FNO")
            .distinct()
            .all()
        )

        fno_symbols = [
            s[0] for s in fno_symbols
            if s[0]
            and len(s[0]) <= 6
            and s[0] not in self.EXCLUDE
        ]

        # Step 2: map to NSE cash market
        nse_stocks = (
            db.query(Instrument)
            .filter(
                Instrument.exchange == "NSE",
                Instrument.symbol.in_(fno_symbols),
            )
            .all()
        )

        return nse_stocks
