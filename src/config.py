from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Paths:
    root: Path = Path(__file__).resolve().parents[1]
    data: Path = root / "data"
    outputs: Path = root / "outputs"
    kpis: Path = outputs / "kpis_parquet"
    reports: Path = outputs / "reports"

@dataclass(frozen=True)
class Params:
    tz: str = "UTC"
    bin_freq: str = "1min"          # time-binning
    realized_lag_s: int = 300        # 5 minutes for realized spread/impact
    winsor_q: float = 0.999          # outlier cap
    min_spread: float = 1e-6
