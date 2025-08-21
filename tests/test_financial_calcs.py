import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from financial_calcs import (
    mrr,
    arr,
    revenue_churn_rate,
    customer_churn_rate,
    arpu,
    ltv,
    cac,
    ltv_cac_ratio,
    gross_margin,
    payback_period,
    burn_multiple,
    conversion_rate,
    retention_rate,
    expansion_revenue,
)


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


def test_subscription_metrics():
    assert mrr(sample_data) == 250
    assert arr(sample_data) == 3000
    assert math.isclose(revenue_churn_rate(sample_data), -0.25, rel_tol=1e-4)
    assert math.isclose(customer_churn_rate(sample_data), 0.1666667, rel_tol=1e-4)
    assert math.isclose(arpu(sample_data), 250 / 150, rel_tol=1e-4)
    assert math.isclose(ltv(sample_data), (250 / 150) / 0.1666667, rel_tol=1e-4)
    assert math.isclose(cac(sample_data), 10.0, rel_tol=1e-4)
    assert math.isclose(ltv_cac_ratio(sample_data), 1.0, rel_tol=1e-4)
    assert math.isclose(gross_margin(sample_data), (3000 - 1000) / 3000, rel_tol=1e-4)
    assert math.isclose(
        payback_period(sample_data),
        10.0 / ((250 / 150) * ((3000 - 1000) / 3000)),
        rel_tol=1e-4,
    )
    assert math.isclose(burn_multiple(sample_data), 200 / 600, rel_tol=1e-4)
    assert math.isclose(conversion_rate(sample_data), 0.5, rel_tol=1e-4)
    assert math.isclose(retention_rate(sample_data), 1 - 0.1666667, rel_tol=1e-4)
    assert expansion_revenue(sample_data) == 400
