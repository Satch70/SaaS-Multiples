import json
import logging
import re
import pymupdf
import pymupdf4llm


logger = logging.getLogger(__name__)


FINANCIAL_TERMS = [
    "total revenue",
    "net income",
    "net loss",
]

VALUE_RE = re.compile(
    r"""
    \$?  # optional dollar sign
    (?:
        -?\d+(?:,\d{3})*(?:\.\d+)?  # optional negative sign with digits
        |\(
            \d+(?:,\d{3})*(?:\.\d+)?  # digits enclosed in parentheses
        \)
    )
    """,
    re.VERBOSE,
)
TERM_RE = re.compile(r"(" + "|".join(re.escape(t) for t in FINANCIAL_TERMS) + r")", re.IGNORECASE)


def extract_financial_info(pdf_path: str, pages=None):
    """Return document metadata and simple financial values.

    The PDF file is opened using :func:`pymupdf.open` as a context manager.
    """
    with pymupdf.open(pdf_path) as doc:
        md_pages = pymupdf4llm.to_markdown(doc, pages=pages, page_chunks=True)

        results = {
            "file_path": pdf_path,
            "doc_metadata": doc.metadata,
            "items": [],
        }

        for page in md_pages:
            page_no = page["metadata"]["page_number"]
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
    """Convert a page range string to a list of 0-based page numbers.

    Accepted formats are a single integer (e.g. ``"3"``) or a range
    ``"start-end"`` where both numbers are 1-based.  A single value will be
    converted to the corresponding zero-based page index, while a range will
    return all pages between ``start`` and ``end`` (inclusive).
    """

    page_range = page_range.strip()

    # Single page specification like ``"3"``
    if re.fullmatch(r"\d+", page_range):
        return [int(page_range) - 1]

    # Range specification like ``"1-5"``
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", page_range)
    if m:
        start, end = int(m.group(1)), int(m.group(2))
        if start > end:
            raise ValueError(f"page range start {start} is greater than end {end}")
        return list(range(start - 1, end))

    raise ValueError(f"Unrecognized page range format: '{page_range}'")


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
