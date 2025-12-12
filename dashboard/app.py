# app.py
import os
import requests
import pandas as pd
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Lumber Risk Sandbox", layout="wide")

st.title("Lumber Risk Sandbox")

st.markdown(
    """
    This dashboard simulates hedging a **long lumber price exposure** using a simple trend rule:

    - You are assumed to be continuously long the underlying lumber exposure.
    - A **70% hedge** is applied on days when the **short moving average** is below the **long moving average** (downtrend signal).
    - **Unhedged P&L** is the cumulative profit and loss of staying fully exposed.
    - **Hedged P&L** is the cumulative profit and loss after applying the 70% hedge rule.
    - **Hedge Vol Reduction** shows how much the hedge reduces the standard deviation of daily P&L.

    Use the controls below to change the moving-average windows and notional exposure, and see how the hedge affects both returns and risk.
    """
)

col1, col2, col3 = st.columns(3)
with col1:
    symbol = st.text_input("Symbol", value="LBS=F")
with col2:
    ma_short = st.number_input("Short MA window", min_value=3, max_value=50, value=10)
with col3:
    ma_long = st.number_input("Long MA window", min_value=10, max_value=200, value=30)

notional = st.number_input(
    "Notional exposure ($)",
    min_value=100_000.0,
    value=1_000_000.0,
    step=100_000.0,
)

st.write("Use the buttons below to refresh data and run analytics.")

if st.button("Run ETL (refresh data)"):
    with st.spinner("Running ETL..."):
        resp = requests.post(f"{API_URL}/etl/run")
        if resp.status_code == 200:
            st.success("ETL completed")
        else:
            st.error(f"ETL failed: {resp.text}")

if st.button("Compute analytics"):
    with st.spinner("Computing..."):
        params = {
            "symbol": symbol,
            "ma_short": ma_short,
            "ma_long": ma_long,
            "notional": notional,
        }
        resp = requests.get(f"{API_URL}/analytics", params=params)
        if resp.status_code != 200:
            st.error(f"Analytics failed: {resp.text}")
        else:
            data = resp.json()
            summary = data["summary"]
            ts = pd.DataFrame(data["timeseries"])

            st.subheader("Summary")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Unhedged P&L", f"${summary['unhedged_pnl']:,.0f}")
            col_b.metric("Hedged P&L", f"${summary['hedged_pnl']:,.0f}")

            if summary["vol_unhedged"] != 0:
                reduction = 1 - summary["vol_hedged"] / summary["vol_unhedged"]
                col_c.metric("Hedge Vol Reduction", f"{reduction:.0%}")
            else:
                col_c.metric("Hedge Vol Reduction", "N/A")

            st.subheader("Price & P&L (recent)")

            ts["trade_date"] = pd.to_datetime(ts["trade_date"])
            ts.set_index("trade_date", inplace=True)

            st.line_chart(ts[["close"]].rename(columns={"close": "Price"}))
            st.line_chart(ts[["pnl_unhedged", "pnl_hedged"]])