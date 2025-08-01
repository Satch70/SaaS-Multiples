import json
from pathlib import Path
from sec_metadata.parser import extract_financial_info, FINANCIAL_TERMS


def main():
    company = input("Enter company name: ").strip()
    folder = Path("reports") / company.replace(" ", "_")
    folder.mkdir(parents=True, exist_ok=True)
    collected = {}

    missing = [t.title() for t in FINANCIAL_TERMS]
    while missing:
        pdf_path = input(
            f"Provide path to PDF with data (missing: {', '.join(missing)}): "
        ).strip()
        if not pdf_path:
            print("No PDF provided. Exiting.")
            return
        data = extract_financial_info(pdf_path)
        for item in data.get("items", []):
            collected.setdefault(item["term"], item["value"])
        missing = [t.title() for t in FINANCIAL_TERMS if t.title() not in collected]
        report_path = folder / "report.md"
        with report_path.open("w", encoding="utf-8") as f:
            f.write(f"# {company} Financial Metrics\n\n")
            for term, value in collected.items():
                f.write(f"- {term}: {value}\n")
        if missing:
            print("Missing information:", ", ".join(missing))
    print("All financial data collected. Report saved at", report_path)


if __name__ == "__main__":
    main()
