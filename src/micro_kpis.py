import numpy as np
import pandas as pd
from .config import Params

def attach_trade_to_quote(trades: pd.DataFrame, quotes: pd.DataFrame) -> pd.DataFrame:
    """
    As-of join: each trade gets the most recent quote (bid/ask/mid) at or before trade time.
    """
    q = quotes[["ts", "etf", "venue", "bid", "ask", "mid"]].sort_values(["etf", "venue", "ts"])
    t = trades.sort_values(["etf", "venue", "ts"]).copy()

    out = pd.merge_asof(
        t,
        q,
        on="ts",
        by=["etf", "venue"],
        direction="backward",
        allow_exact_matches=True,
    )
    return out

def compute_trade_kpis(trades_with_q: pd.DataFrame, quotes: pd.DataFrame, p: Params) -> pd.DataFrame:
    """
    KPIs (trade-based):
      - effective_spread: 2*|P - mid| / mid
      - realized_spread: 2*sign*(P - mid_{t+lag}) / mid_t
      - price_impact: sign*(mid_{t+lag} - mid_t) / mid_t
    """
    df = trades_with_q.copy()
    df = df.dropna(subset=["mid", "bid", "ask"])

    # trade sign: use provided side if exists, else infer from Lee-Ready-like midpoint rule
    if "side" in df.columns:
        side = df["side"].astype(str).str.upper()
        df["sign"] = np.where(side.str.startswith("B"), 1.0, np.where(side.str.startswith("S"), -1.0, np.nan))
    else:
        df["sign"] = np.where(df["price"] >= df["mid"], 1.0, -1.0)

    df["effective_spread"] = 2.0 * (df["price"] - df["mid"]).abs() / df["mid"]

    # get mid at t+lag using asof on quotes shifted in time
    q = quotes[["ts", "etf", "venue", "mid"]].copy().sort_values(["etf", "venue", "ts"])
    q_lag = q.copy()
    q_lag["ts"] = q_lag["ts"] - pd.Timedelta(seconds=p.realized_lag_s)  # so asof at trade time returns mid_{t+lag}
    q_lag = q_lag.rename(columns={"mid": "mid_fwd"})

    df = df.sort_values(["etf", "venue", "ts"])
    df = pd.merge_asof(df, q_lag, on="ts", by=["etf", "venue"], direction="forward", allow_exact_matches=True)

    df["realized_spread"] = 2.0 * df["sign"] * (df["price"] - df["mid_fwd"]) / df["mid"]
    df["price_impact"] = df["sign"] * (df["mid_fwd"] - df["mid"]) / df["mid"]

    return df

def compute_quote_kpis(quotes: pd.DataFrame) -> pd.DataFrame:
    """
    KPIs (quote-based):
      - quoted_depth: bid_size + ask_size
      - rel_spread: (ask-bid)/mid
      - microprice: (ask*bid_size + bid*ask_size)/(bid_size+ask_size)
      - vol_1m: rolling 1-minute mid volatility proxy after resample
    """
    q = quotes.copy()
    q["quoted_depth"] = q["bid_size"].clip(lower=0) + q["ask_size"].clip(lower=0)
    q["rel_spread"] = (q["ask"] - q["bid"]) / q["mid"]
    denom = (q["bid_size"] + q["ask_size"]).replace(0, np.nan)
    q["microprice"] = (q["ask"] * q["bid_size"] + q["bid"] * q["ask_size"]) / denom
    return q
