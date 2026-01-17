import pandas as pd
from pathlib import Path

def read_quotes(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # required: ts, etf, venue, bid, ask, bid_size, ask_size
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df.sort_values(["etf", "venue", "ts"]).reset_index(drop=True)

def read_trades(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # required: ts, etf, venue, price, size, side (B/S optional)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df.sort_values(["etf", "venue", "ts"]).reset_index(drop=True)
