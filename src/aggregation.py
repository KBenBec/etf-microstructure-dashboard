import pandas as pd
import numpy as np
from .config import Params

def time_bin_quotes(quotes_k: pd.DataFrame, p: Params) -> pd.DataFrame:
    q = quotes_k.copy()
    q["bin"] = q["ts"].dt.floor(p.bin_freq)

    agg = (q.groupby(["etf", "venue", "bin"])
             .agg(
                 mid=("mid", "median"),
                 spread=("spread", "median"),
                 rel_spread=("rel_spread", "median"),
                 quoted_depth=("quoted_depth", "median"),
                 microprice=("microprice", "median"),
                 n_quotes=("mid", "size"),
             )
             .reset_index())

    # volatility buckets on binned mid
    agg = agg.sort_values(["etf", "venue", "bin"])
    agg["ret"] = agg.groupby(["etf", "venue"])["mid"].pct_change()
    agg["vol"] = agg.groupby(["etf", "venue"])["ret"].rolling(30, min_periods=10).std().reset_index(level=[0,1], drop=True)
    agg["vol_bucket"] = pd.cut(
        agg["vol"],
        bins=[-np.inf, 0.0005, 0.001, 0.002, np.inf],
        labels=["low", "mid", "high", "extreme"],
    )
    return agg

def time_bin_trades(trades_k: pd.DataFrame, p: Params) -> pd.DataFrame:
    t = trades_k.copy()
    t["bin"] = t["ts"].dt.floor(p.bin_freq)

    agg = (t.groupby(["etf", "venue", "bin"])
             .agg(
                 eff_spread=("effective_spread", "mean"),
                 real_spread=("realized_spread", "mean"),
                 impact=("price_impact", "mean"),
                 n_trades=("price", "size"),
                 notional=("price", lambda x: float(np.nan)),  # placeholder if you want price*size with access to size
             )
             .reset_index())
    return agg
