import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import Price

def get_price_df(symbol: str = "LBS=F") -> pd.DataFrame:
    session: Session = SessionLocal()
    try:
        rows = (
            session.query(Price)
            .filter(Price.symbol == symbol)
            .order_by(Price.trade_date)
            .all()
        )
    finally:
        session.close()

    if not rows:
        return pd.DataFrame()

    data = [
        {
            "trade_date": r.trade_date,
            "close": r.close,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    df.set_index("trade_date", inplace=True)
    return df

def compute_analytics(symbol: str = "LBS=F",
                      ma_short: int = 10,
                      ma_long: int = 30,
                      notional_exposure: float = 1_000_000.0):
    df = get_price_df(symbol)
    if df.empty:
        return {}

    df["ret"] = df["close"].pct_change()
    df["ma_short"] = df["close"].rolling(ma_short).mean()
    df["ma_long"] = df["close"].rolling(ma_long).mean()

    # always long physical
    df["pnl_unhedged"] = df["ret"].fillna(0) * notional_exposure

    # toy hedge: when short MA < long MA, we hedge 70% of exposure
    df["hedged_flag"] = (df["ma_short"] < df["ma_long"]).astype(int)
    hedge_ratio = 0.7
    df["pnl_hedged"] = df["pnl_unhedged"] * (1 - hedge_ratio * df["hedged_flag"])

    summary = {
        "symbol": symbol,
        "start_date": str(df.index.min()),
        "end_date": str(df.index.max()),
        "unhedged_pnl": float(df["pnl_unhedged"].sum()),
        "hedged_pnl": float(df["pnl_hedged"].sum()),
        "vol_unhedged": float(df["pnl_unhedged"].std()),
        "vol_hedged": float(df["pnl_hedged"].std()),
    }

    ts = df.tail(100).reset_index().to_dict(orient="records")

    return {
        "summary": summary,
        "timeseries": ts,
    }