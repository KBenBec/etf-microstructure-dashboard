import pandas as pd
from src.micro_kpis import compute_quote_kpis

def test_quote_kpis_shapes():
    q = pd.DataFrame({
        "ts": pd.to_datetime(["2026-01-01T09:00:00Z", "2026-01-01T09:00:01Z"]),
        "etf": ["ETF01", "ETF01"],
        "venue": ["V1", "V1"],
        "bid": [99.9, 99.8],
        "ask": [100.1, 100.2],
        "bid_size": [100, 120],
        "ask_size": [110, 90],
        "mid": [100.0, 100.0],
        "spread": [0.2, 0.4],
    })
    out = compute_quote_kpis(q)
    assert "rel_spread" in out.columns
    assert "quoted_depth" in out.columns
    assert out["quoted_depth"].min() > 0
