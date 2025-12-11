import datetime as dt
import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from .db import SessionLocal, engine, Base
from .models import Price

def init_db():
    Base.metadata.create_all(bind=engine)

def fetch_lumber_data(symbol: str = "LBS=F",
                      start: str = "2020-01-01",
                      end: str | None = None) -> pd.DataFrame:
    if end is None:
        end = dt.date.today().isoformat()

    data = yf.download(symbol, start=start, end=end)
    if data.empty:
        raise ValueError("No data returned from market data API")

    # Reset index so the date becomes a column
    data = data.copy().reset_index()

    # If we got a MultiIndex (Price, Ticker), flatten it
    if isinstance(data.columns, pd.MultiIndex):
        # take the first level (Price) and lowercase it
        data.columns = [str(col[0]).lower() for col in data.columns]
    else:
        # single index – just lowercase everything
        data.rename(columns=str.lower, inplace=True)

    # Rename the date column consistently
    if "date" in data.columns:
        data.rename(columns={"date": "trade_date"}, inplace=True)
    elif "datetime" in data.columns:
        data.rename(columns={"datetime": "trade_date"}, inplace=True)

    # Now we expect these columns to exist
    expected_cols = ["trade_date", "open", "high", "low", "close", "volume"]
    missing = [c for c in expected_cols if c not in data.columns]
    if missing:
        raise RuntimeError(f"Missing expected columns {missing}. Got: {list(data.columns)}")

    # Return only what we need, with flat string column names
    return data[expected_cols]

def load_to_db(df: pd.DataFrame, symbol: str):
    session: Session = SessionLocal()
    try:
        # wipe existing rows for this symbol for a clean demo
        session.query(Price).filter(Price.symbol == symbol).delete()
        session.commit()

        records = df.to_dict(orient="records")

        for row in records:
            trade_date = row["trade_date"]
            if hasattr(trade_date, "date"):
                trade_date = trade_date.date()

            # volume can be missing or NaN
            volume_raw = row.get("volume", None)
            if volume_raw is None or (isinstance(volume_raw, float) and pd.isna(volume_raw)):
                volume_val = None
            else:
                volume_val = float(volume_raw)

            price = Price(
                symbol=symbol,
                trade_date=trade_date,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=volume_val,
            )
            session.add(price)
        session.commit()
    finally:
        session.close()

def run_etl():
    init_db()
    symbol = "LBS=F"
    df = fetch_lumber_data(symbol)
    load_to_db(df, symbol)

if __name__ == "__main__":
    run_etl()
    print("ETL complete.")