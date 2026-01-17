import pandas as pd
from pathlib import Path

def save_parquet(df: pd.DataFrame, out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path

def save_html_table(df: pd.DataFrame, out_path: Path, title: str = "Summary") -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = f"<h2>{title}</h2>" + df.to_html(index=False)
    out_path.write_text(html, encoding="utf-8")
