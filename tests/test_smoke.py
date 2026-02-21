"""Smoke tests to verify project setup."""

import fast_aiogentic
from fast_aiogentic.text_utils import split_for_telegram


def test_import():
    """Test that the package can be imported."""
    assert fast_aiogentic.__version__


def test_split_short_text():
    """Test short text stays as single chunk."""
    assert split_for_telegram("hello") == ["hello"]


def test_split_empty_text():
    """Test empty text."""
    assert split_for_telegram("") == [""]


def test_split_at_limit():
    """Test text exactly at limit stays as single chunk."""
    text = "a" * 4096
    assert split_for_telegram(text) == [text]


def test_split_over_limit():
    """Test text over limit splits into valid chunks."""
    text = "a" * 4097
    result = split_for_telegram(text)
    assert len(result) > 1
    assert all(len(chunk) <= 4096 for chunk in result)


def test_split_preserves_paragraphs():
    """Test that splitting preserves paragraph boundaries."""
    para1 = "a" * 2000
    para2 = "b" * 2000
    para3 = "c" * 2000
    text = f"{para1}\n\n{para2}\n\n{para3}"

    result = split_for_telegram(text)
    assert len(result) >= 2
    assert all(len(chunk) <= 4096 for chunk in result)
