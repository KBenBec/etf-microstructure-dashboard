from src.config import Paths, Params
from src.io_data import read_quotes, read_trades
from src.preprocess import clean_quotes, clean_trades
from src.micro_kpis import attach_trade_to_quote, compute_trade_kpis, compute_quote_kpis
from src.aggregation import time_bin_quotes, time_bin_trades
from src.reporting import save_parquet, save_html_table

def main():
    paths, p = Paths(), Params()

    quotes = read_quotes(paths.data / "sample_quotes.csv")
    trades = read_trades(paths.data / "sample_trades.csv")

    quotes_c = clean_quotes(quotes, p)
    trades_c = clean_trades(trades, p)

    quotes_k = compute_quote_kpis(quotes_c)
    trades_q = attach_trade_to_quote(trades_c, quotes_c)
    trades_k = compute_trade_kpis(trades_q, quotes_c, p)

    q_bin = time_bin_quotes(quotes_k, p)
    t_bin = time_bin_trades(trades_k, p)

    kpis = q_bin.merge(t_bin, on=["etf", "venue", "bin"], how="left")
    save_parquet(kpis, paths.kpis, "kpis_binned")

    summary = (kpis.groupby(["etf", "venue"])
                    .agg(
                        rel_spread=("rel_spread", "median"),
                        depth=("quoted_depth", "median"),
                        eff_spread=("eff_spread", "mean"),
                        impact=("impact", "mean"),
                        n_bins=("bin", "count"),
                    )
                    .reset_index())
    save_html_table(summary, paths.reports / "summary.html", title="ETF Microstructure Summary")

    print("Done. outputs/ created.")

if __name__ == "__main__":
    main()
