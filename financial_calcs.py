"""Financial metric calculations."""
from typing import List, Dict


def parse_value(value: str) -> float:
    """Convert a string like "$1,234" or "(100)" to a float."""
    value = value.strip().replace("$", "").replace(",", "")
    if value.endswith("%"):
        return float(value[:-1]) / 100
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1]
        return -float(value)
    return float(value)


def discounted_cash_flow(cash_flows: List[float], discount_rate: float, terminal_growth: float = 0.02) -> float:
    """Simple DCF calculation using provided cash flows."""
    dcf = 0.0
    for i, cf in enumerate(cash_flows, start=1):
        dcf += cf / (1 + discount_rate) ** i
    terminal_value = cash_flows[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    dcf += terminal_value / (1 + discount_rate) ** len(cash_flows)
    return dcf


def ebitda_margin(revenue: float, ebitda: float) -> float:
    return ebitda / revenue if revenue else 0.0


def revenue_cagr(revenues: List[float]) -> float:
    if len(revenues) < 2:
        return 0.0
    start, end = revenues[0], revenues[-1]
    years = len(revenues) - 1
    return (end / start) ** (1 / years) - 1

# Mapping of metric names to callables. Each callable receives a dict of data by year.
def _sorted_years(data: Dict[str, Dict[str, str]]):
    return sorted(data.keys(), key=int)


METRICS = {
    "DCF": lambda data: discounted_cash_flow(
        [parse_value(data[y].get("Net Income", "0")) for y in _sorted_years(data)], 0.1
    ),
    "EBITDA Margin": lambda data: ebitda_margin(
        parse_value(data[_sorted_years(data)[-1]].get("Total Revenue", "0")),
        parse_value(data[_sorted_years(data)[-1]].get("EBITDA", "0")),
    ),
    "Revenue CAGR": lambda data: revenue_cagr(
        [parse_value(data[y].get("Total Revenue", "0")) for y in _sorted_years(data)]
    ),
}
