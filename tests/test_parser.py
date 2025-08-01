import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sec_metadata.parser import VALUE_RE

@pytest.mark.parametrize(
    "text,expected",
    [
        ("Revenue was 1000", "1000"),
        ("Loss was -1000", "-1000"),
        ("Loss was (1000)", "(1000)"),
        ("Loss was $(1000)", "$(1000)"),
        ("Income was $-1,000", "$-1,000"),
        ("Revenue was 1,000", "1,000"),
    ],
)
def test_value_re(text, expected):
    match = VALUE_RE.search(text)
    assert match is not None
    assert match.group(0) == expected

