import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="ETF Microstructure Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
KPI_PATH = ROOT / "outputs" / "kpis_parquet" / "kpis_binned.parquet"

st.title("ETF Market Quality & Microstructure Dashboard")

if not KPI_PATH.exists():
    st.warning("No KPI file found. Run: python examples/run_pipeline.py")
    st.stop()

df = pd.read_parquet(KPI_PATH)
df["bin"] = pd.to_datetime(df["bin"], utc=True)

etfs = sorted(df["etf"].unique())
venues = sorted(df["venue"].unique())

c1, c2, c3 = st.columns(3)
etf = c1.selectbox("ETF", etfs, index=0)
venue = c2.selectbox("Venue", venues, index=0)

sub = df[(df["etf"] == etf) & (df["venue"] == venue)].sort_values("bin")

c3.metric("Bins", f"{len(sub):,}")

st.subheader("Time-series (binned)")
st.line_chart(sub.set_index("bin")[["rel_spread", "quoted_depth"]])

st.subheader("Execution proxies (trade-based)")
st.line_chart(sub.set_index("bin")[["eff_spread", "real_spread", "impact"]])

st.subheader("Quick table")
st.dataframe(sub.tail(200), use_container_width=True)
