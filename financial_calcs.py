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


def mrr(data: Dict[str, Dict[str, str]]) -> float:
    """Monthly recurring revenue derived from MRR or ARR fields."""
    years = _sorted_years(data)
    latest = data[years[-1]] if years else {}
    if "MRR" in latest:
        return parse_value(latest["MRR"])
    if "ARR" in latest:
        return parse_value(latest["ARR"]) / 12
    return parse_value(latest.get("Total Revenue", "0")) / 12


def arr(data: Dict[str, Dict[str, str]]) -> float:
    """Annual recurring revenue derived from ARR or MRR fields."""
    years = _sorted_years(data)
    latest = data[years[-1]] if years else {}
    if "ARR" in latest:
        return parse_value(latest["ARR"])
    if "MRR" in latest:
        return parse_value(latest["MRR"]) * 12
    return parse_value(latest.get("Total Revenue", "0"))


def revenue_churn_rate(data: Dict[str, Dict[str, str]]) -> float:
    """Simple revenue churn based on year-over-year change."""
    years = _sorted_years(data)
    if len(years) < 2:
        return 0.0
    prev = parse_value(data[years[-2]].get("Total Revenue", "0"))
    curr = parse_value(data[years[-1]].get("Total Revenue", "0"))
    return (prev - curr) / prev if prev else 0.0


def customer_churn_rate(data: Dict[str, Dict[str, str]]) -> float:
    """Churn based on customer counts and new additions."""
    years = _sorted_years(data)
    if len(years) < 2:
        return 0.0
    prev = parse_value(data[years[-2]].get("Customers", "0"))
    curr_year = data[years[-1]]
    curr = parse_value(curr_year.get("Customers", "0"))
    new_customers = parse_value(curr_year.get("New Customers", "0"))
    return (prev + new_customers - curr) / prev if prev else 0.0


def arpu(data: Dict[str, Dict[str, str]]) -> float:
    """Average revenue per user using MRR and customer count."""
    years = _sorted_years(data)
    latest = data[years[-1]] if years else {}
    customers = parse_value(latest.get("Customers", "0"))
    mrr_value = mrr(data)
    return mrr_value / customers if customers else 0.0


def ltv(data: Dict[str, Dict[str, str]]) -> float:
    """Customer lifetime value = ARPU / churn rate."""
    churn = customer_churn_rate(data)
    arpu_value = arpu(data)
    return arpu_value / churn if churn else 0.0


def cac(data: Dict[str, Dict[str, str]]) -> float:
    """Customer acquisition cost."""
    years = _sorted_years(data)
    latest = data[years[-1]] if years else {}
    marketing = parse_value(latest.get("Sales and Marketing", "0"))
    new_customers = parse_value(latest.get("New Customers", "0"))
    return marketing / new_customers if new_customers else 0.0


def ltv_cac_ratio(data: Dict[str, Dict[str, str]]) -> float:
    """Efficiency of customer acquisition."""
    cac_value = cac(data)
    ltv_value = ltv(data)
    return ltv_value / cac_value if cac_value else 0.0


def gross_margin(data: Dict[str, Dict[str, str]]) -> float:
    """Gross margin = (revenue - cost) / revenue."""
    years = _sorted_years(data)
    latest = data[years[-1]] if years else {}
    revenue = parse_value(latest.get("Total Revenue", "0"))
    cost = parse_value(latest.get("Cost of Revenue", "0"))
    return (revenue - cost) / revenue if revenue else 0.0


def payback_period(data: Dict[str, Dict[str, str]]) -> float:
    """Months to recover CAC using ARPU and gross margin."""
    cac_value = cac(data)
    arpu_value = arpu(data)
    margin = gross_margin(data)
    monthly_gross_profit = arpu_value * margin
    return cac_value / monthly_gross_profit if monthly_gross_profit else 0.0


def burn_multiple(data: Dict[str, Dict[str, str]]) -> float:
    """Net burn divided by net new ARR."""
    years = _sorted_years(data)
    latest = data[years[-1]] if years else {}
    burn = parse_value(latest.get("Net Burn", "0"))
    net_new_arr = parse_value(latest.get("Net New ARR", "0"))
    return burn / net_new_arr if net_new_arr else 0.0


def conversion_rate(data: Dict[str, Dict[str, str]]) -> float:
    """Conversion of free to paid users."""
    years = _sorted_years(data)
    latest = data[years[-1]] if years else {}
    paid = parse_value(latest.get("Paid Users", "0"))
    total = parse_value(latest.get("Total Users", "0"))
    return paid / total if total else 0.0


def retention_rate(data: Dict[str, Dict[str, str]]) -> float:
    """Retention as complement of churn."""
    return 1 - customer_churn_rate(data)


def expansion_revenue(data: Dict[str, Dict[str, str]]) -> float:
    """Revenue from existing customers beyond starting cohort."""
    years = _sorted_years(data)
    if len(years) < 2:
        return 0.0
    prev = parse_value(data[years[-2]].get("Existing Customer Revenue", "0"))
    curr = parse_value(data[years[-1]].get("Existing Customer Revenue", "0"))
    return curr - prev

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
    "MRR": mrr,
    "ARR": arr,
    "Revenue Churn": revenue_churn_rate,
    "Customer Churn": customer_churn_rate,
    "LTV": ltv,
    "CAC": cac,
    "LTV:CAC": ltv_cac_ratio,
    "Gross Margin": gross_margin,
    "Payback Period": payback_period,
    "Burn Multiple": burn_multiple,
    "ARPU": arpu,
    "Conversion Rate": conversion_rate,
    "Retention": retention_rate,
    "Expansion Revenue": expansion_revenue,
}
