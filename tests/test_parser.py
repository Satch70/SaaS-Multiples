import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import fitz
import pytest
import pymupdf4llm
from sec_metadata import extract_financial_info


SAMPLE_PDF = os.path.join(os.path.dirname(__file__), 'data', 'sample.pdf')


def test_extract_financial_info_success():
    result = extract_financial_info(SAMPLE_PDF)
    assert result['doc_metadata']['title'] == 'Sample Filing'
    terms = {(item['term'], item['value']) for item in result['items']}
    assert ('Total Revenue', '$10,000') in terms
    assert ('Net Income', '$2,000') in terms


def test_missing_metadata(monkeypatch):
    real_to_md = pymupdf4llm.to_markdown

    def fake_to_markdown(doc, *args, **kwargs):
        result = real_to_md(doc, *args, **kwargs)
        # simulate missing metadata after extraction
        doc.metadata = {}
        return result

    monkeypatch.setattr(pymupdf4llm, "to_markdown", fake_to_markdown)
    result = extract_financial_info(SAMPLE_PDF)
    assert result['doc_metadata'] == {}
    # terms should still be extracted
    assert any(item['term'] == 'Total Revenue' for item in result['items'])


