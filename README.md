# SaaS Multiples

This repository provides a small utility for extracting metadata and basic financial
information from SEC filing PDFs. It uses [PyMuPDF4LLM](https://github.com/ArtifexSoftware/pymupdf4llm) from Artifex to convert PDF pages to markdown and searches the text for
common financial terms such as **Total Revenue** or **Net Income**.

## Installation

Create a Python virtual environment and install dependencies. The project
requires `pymupdf4llm` version `0.0.20` or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Check the installed version and upgrade if it is older than `0.0.20`:

```bash
python -c "import pymupdf4llm; print(pymupdf4llm.version)"
```

If the printed version is lower than `0.0.20`, run:

```bash
pip install -U pymupdf4llm
```

## Usage

Run the parser on a SEC filing PDF:

```bash
python sec_metadata/parser.py path/to/filing.pdf --pages 1-5
```

The `--pages` option accepts a single page number like `3` or a
range such as `1-5`.  Numbers are 1-based and the range's start must
not exceed its end.  Any other format will raise a `ValueError`.

This will print a JSON structure containing the document's metadata along with any
financial terms discovered in the given pages.

### Multi-company metrics

To compare SaaS metrics across multiple companies, set an
Alpha Vantage API key in the environment and run the table generator:

```bash
export ALPHAVANTAGE_API_KEY=your_key
python metrics_table.py AAPL MSFT --out metrics.csv
```

The command writes a CSV file and a Markdown companion containing values
for metrics such as MRR, churn, LTV, CAC, and more.


## Running Tests

After installing the requirements, run the test suite with:

```bash
pytest
```
