import csv
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from metrics_table import compute_metrics_table

sample_data = {
    "2022": {
        "Total Revenue": "2400",
        "Cost of Revenue": "800",
        "Customers": "120",
        "Existing Customer Revenue": "1800",
    },
    "2023": {
        "Total Revenue": "3000",
        "Cost of Revenue": "1000",
        "Customers": "150",
        "New Customers": "50",
        "Sales and Marketing": "500",
        "Net Burn": "200",
        "Net New ARR": "600",
        "Paid Users": "150",
        "Total Users": "300",
        "Existing Customer Revenue": "2200",
        "MRR": "250",
    },
}


def test_generate_table(tmp_path: Path):
    out = tmp_path / "metrics.csv"
    with patch("metrics_table.fetch_company_data", return_value=sample_data):
        compute_metrics_table(["TST"], out)
    assert out.exists()
    with out.open() as f:
        rows = list(csv.reader(f))
    assert rows[0][0] == "Ticker"
    assert rows[1][0] == "TST"
    arr_index = rows[0].index("ARR")
    assert rows[1][arr_index] == "3000.00"
