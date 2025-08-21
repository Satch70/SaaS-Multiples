"""Interactive utility to collect financial data and generate reports."""
from pathlib import Path
from typing import Dict

from sec_metadata.parser import extract_financial_info
from financial_calcs import METRICS, parse_value, _sorted_years

YEARS = 5


def collect_filings(years: int = YEARS) -> Dict[str, Dict[str, str]]:
    data_by_year: Dict[str, Dict[str, str]] = {}
    for _ in range(years):
        year = input("Enter filing year (e.g. 2023): ").strip()
        pdf_path = input(f"Path to PDF for {year}: ").strip()
        if not pdf_path:
            continue
        info = extract_financial_info(pdf_path)
        items = {item["term"]: item["value"] for item in info.get("items", [])}
        data_by_year[year] = items
    return data_by_year


def prompt_metrics(data_by_year: Dict[str, Dict[str, str]]):
    results = {}
    years = _sorted_years(data_by_year)
    latest_data = data_by_year[years[-1]] if years else {}
    # First handle calculated metrics
    for name, func in METRICS.items():
        ans = input(f"Calculate {name}? (y/n): ").strip().lower()
        if ans == "y":
            results[name] = {"value": func(data_by_year), "source": "calculated"}
    # Then allow including raw terms directly from filings
    for term in ["EBITDA", "Net Income", "Total Revenue"]:
        ans = input(f"Include {term}? (y/n): ").strip().lower()
        if ans == "y" and term in latest_data:
            results[term] = {
                "value": parse_value(latest_data[term]),
                "source": "from filing",
            }
    return results


def write_report(
    company: str,
    data_by_year: Dict[str, Dict[str, str]],
    metrics: Dict[str, Dict[str, float]],
    folder: Path,
) -> Path:
    report_path = folder / "report.md"
    years = _sorted_years(data_by_year)
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"# {company} Financial Report\n\n")
        f.write("## Financial Statements (5-year summary)\n\n")
        terms = sorted({term for year in data_by_year.values() for term in year})
        for term in terms:
            f.write(f"### {term}\n")
            for year in years:
                value = data_by_year[year].get(term, "N/A")
                f.write(f"- {year}: {value} (from filing)\n")
            f.write("\n")
        if metrics:
            f.write("## Metrics\n\n")
            for name, info in metrics.items():
                value = info["value"]
                if isinstance(value, float):
                    f.write(f"- {name}: {value:.2f} ({info['source']})\n")
                else:
                    f.write(f"- {name}: {value} ({info['source']})\n")
    return report_path


def main():
    company = input("Enter company name: ").strip()
    folder = Path("reports") / company.replace(" ", "_")
    folder.mkdir(parents=True, exist_ok=True)
    data = collect_filings()
    metrics = prompt_metrics(data)
    path = write_report(company, data, metrics, folder)
    print("Report saved at", path)


if __name__ == "__main__":
    main()
