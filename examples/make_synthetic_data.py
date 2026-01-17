import numpy as np
import pandas as pd
from pathlib import Path

def make_synthetic(out_dir: Path, n_etf=5, n_venues=3, minutes=240, seed=7):
    rng = np.random.default_rng(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    etfs = [f"ETF{i:02d}" for i in range(1, n_etf+1)]
    venues = [f"VENUE{j}" for j in range(1, n_venues+1)]
    start = pd.Timestamp("2026-01-02 09:00:00", tz="UTC")

    quote_rows = []
    trade_rows = []

    for etf in etfs:
        base = 100 + rng.normal(0, 1)
        for venue in venues:
            mid = base + rng.normal(0, 0.2)
            for m in range(minutes):
                ts = start + pd.Timedelta(minutes=m)
                # random walk mid
                mid *= (1 + rng.normal(0, 0.0003))
                spread = abs(rng.normal(0.01, 0.003))
                bid = mid - spread/2
                ask = mid + spread/2
                bid_size = int(rng.integers(50, 500))
                ask_size = int(rng.integers(50, 500))
                quote_rows.append([ts.isoformat(), etf, venue, bid, ask, bid_size, ask_size])

                # a few trades per minute
                ntr = int(rng.integers(0, 4))
                for _ in range(ntr):
                    side = "B" if rng.random() < 0.5 else "S"
                    px = ask if side == "B" else bid
                    px = px * (1 + rng.normal(0, 0.0001))
                    size = int(rng.integers(10, 200))
                    trade_rows.append([ts.isoformat(), etf, venue, px, size, side])

    quotes = pd.DataFrame(quote_rows, columns=["ts", "etf", "venue", "bid", "ask", "bid_size", "ask_size"])
    trades = pd.DataFrame(trade_rows, columns=["ts", "etf", "venue", "price", "size", "side"])

    quotes.to_csv(out_dir / "sample_quotes.csv", index=False)
    trades.to_csv(out_dir / "sample_trades.csv", index=False)

if __name__ == "__main__":
    make_synthetic(Path(__file__).resolve().parents[1] / "data")
    print("Synthetic data written to /data.")
