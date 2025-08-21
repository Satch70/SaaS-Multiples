"""Fetch financial data for companies from a public API."""
from __future__ import annotations

import os
import time
from typing import Dict

import requests

API_URL = "https://www.alphavantage.co/query"


def fetch_company_data(ticker: str, api_key: str | None = None, retries: int = 3, pause: float = 1.0) -> Dict[str, Dict[str, str]]:
    """Retrieve basic financial inputs for a ticker.

    Parameters
    ----------
    ticker: str
        Stock ticker symbol.
    api_key: str | None
        Alpha Vantage API key. Falls back to the ``ALPHAVANTAGE_API_KEY``
        environment variable or ``"demo"`` if not provided.
    retries: int
        Number of attempts before giving up.
    pause: float
        Seconds to wait between retries.

    Returns
    -------
    dict
        A mapping of years to financial terms. Currently only a ``"latest"``
        entry is returned, containing revenue and other basic metrics.
    """

    api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY", "demo")
    params = {"function": "OVERVIEW", "symbol": ticker, "apikey": api_key}
    for _ in range(retries):
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            if resp.ok:
                data = resp.json()
                if data:
                    revenue = data.get("RevenueTTM", "0")
                    gross_profit = data.get("GrossProfitTTM", "0")
                    try:
                        cost_of_revenue = str(float(revenue) - float(gross_profit))
                    except (TypeError, ValueError):
                        cost_of_revenue = "0"
                    return {
                        "latest": {
                            "Total Revenue": revenue,
                            "Cost of Revenue": cost_of_revenue,
                            # Placeholder fields the API does not provide.
                            "Customers": data.get("FullTimeEmployees", "0"),
                            "New Customers": "0",
                            "Sales and Marketing": "0",
                            "Net Burn": "0",
                            "Net New ARR": "0",
                            "Paid Users": "0",
                            "Total Users": "0",
                            "Existing Customer Revenue": revenue,
                        }
                    }
        except requests.RequestException:
            pass
        time.sleep(pause)
    raise RuntimeError(f"Unable to fetch data for {ticker}")
