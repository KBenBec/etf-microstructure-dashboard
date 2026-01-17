import numpy as np
import pandas as pd
from .config import Params

def _winsorize(s: pd.Series, q: float) -> pd.Series:
    if s.dropna().empty:
        return s
    hi = s.quantile(q)
    lo = s.quantile(1 - q)
    return s.clip(lower=lo, upper=hi)

def clean_quotes(quotes: pd.DataFrame, p: Params) -> pd.DataFrame:
    q = quotes.copy()

    # basic sanity
    q = q[(q["bid"] > 0) & (q["ask"] > 0)]
    q = q[q["ask"] > q["bid"]]

    # spread + mid
    q["mid"] = 0.5 * (q["bid"] + q["ask"])
    q["spread"] = (q["ask"] - q["bid"]).clip(lower=p.min_spread)

    # outlier control
    q["mid"] = _winsorize(q["mid"], p.winsor_q)
    q["spread"] = _winsorize(q["spread"], p.winsor_q)

    # session alignment (simple example: keep 08:00–17:30 UTC)
    t = q["ts"].dt.tz_convert(p.tz)
    q = q[(t.dt.hour >= 8) & ((t.dt.hour < 17) | ((t.dt.hour == 17) & (t.dt.minute <= 30)))]

    return q.reset_index(drop=True)

def clean_trades(trades: pd.DataFrame, p: Params) -> pd.DataFrame:
    t = trades.copy()
    t = t[(t["price"] > 0) & (t["size"] > 0)]
    t["price"] = _winsorize(t["price"], p.winsor_q)

    # session alignment consistent with quotes
    ts = t["ts"].dt.tz_convert(p.tz)
    t = t[(ts.dt.hour >= 8) & ((ts.dt.hour < 17) | ((ts.dt.hour == 17) & (ts.dt.minute <= 30)))]

    return t.reset_index(drop=True)
