import json
import re
import pymupdf
import pymupdf4llm


FINANCIAL_TERMS = [
    "total revenue",
    "net income",
    "net loss",
]

VALUE_RE = re.compile(r"\$?\(?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?")
TERM_RE = re.compile(r"(" + "|".join(re.escape(t) for t in FINANCIAL_TERMS) + r")", re.IGNORECASE)


def extract_financial_info(pdf_path: str, pages=None):
    """Return document metadata and simple financial values."""
    doc = pymupdf.open(pdf_path)
    md_pages = pymupdf4llm.to_markdown(doc, pages=pages, page_chunks=True)

    results = {
        "file_path": pdf_path,
        "doc_metadata": doc.metadata,
        "items": [],
    }

    for page in md_pages:
        meta = page.get("metadata", {})
        page_no = meta.get("page_number") or meta.get("page")
        for line in page["text"].splitlines():
            term_match = TERM_RE.search(line)
            if term_match:
                value_match = VALUE_RE.search(line)
                if value_match:
                    results["items"].append(
                        {
                            "page": page_no,
                            "term": term_match.group(1).title(),
                            "value": value_match.group(0),
                        }
                    )
    return results


def parse_page_range(page_range: str):
    """Convert a 1-based page range like '1-3' to a list of 0-based pages."""
    start, end = [int(p) for p in page_range.split("-", 1)]
    return list(range(start - 1, end))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract metadata and financial terms from a SEC filing PDF"
    )
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument(
        "--pages",
        help="Optional page range like '1-10'",
    )
    args = parser.parse_args()

    pages = parse_page_range(args.pages) if args.pages else None
    data = extract_financial_info(args.pdf, pages=pages)
    print(json.dumps(data, indent=2))
