"""Generate tables of financial metrics for multiple companies."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from company_data import fetch_company_data
from financial_calcs import METRICS


def compute_metrics_table(tickers: List[str], out_file: Path) -> Path:
    """Fetch data for each ticker, compute metrics, and write a CSV/Markdown table."""
    header = ["Ticker"] + list(METRICS.keys())
    rows = []
    for ticker in tickers:
        data = fetch_company_data(ticker)
        metrics = {name: func(data) for name, func in METRICS.items()}
        row = [ticker]
        for name in METRICS.keys():
            val = metrics.get(name, "")
            if isinstance(val, float):
                row.append(f"{val:.2f}")
            else:
                row.append(str(val))
        rows.append(row)
    with out_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    md_path = out_file.with_suffix(".md")
    with md_path.open("w", encoding="utf-8") as f:
        f.write("|" + "|".join(header) + "|\n")
        f.write("|" + "|".join(["---"] * len(header)) + "|\n")
        for row in rows:
            f.write("|" + "|".join(row) + "|\n")
    return out_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate metrics table for tickers")
    parser.add_argument("tickers", nargs="+", help="Stock tickers")
    parser.add_argument("--out", default="metrics.csv", help="Output CSV file")
    args = parser.parse_args()
    compute_metrics_table(args.tickers, Path(args.out))


if __name__ == "__main__":
    main()
