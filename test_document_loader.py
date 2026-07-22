"""
Unit tests for document_loader.py.
These tests only exercise loading/splitting logic and do not call the
OpenAI API, so they run without an API key.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.document_loader import load_and_split, load_documents, split_documents

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"


def test_load_documents_finds_sample_files():
    docs = load_documents(DOCS_DIR)
    assert len(docs) >= 4, "Expected at least 4 sample documents to load"
    filenames = {doc.metadata["source_file"] for doc in docs}
    assert "quarterly_sales_report.txt" in filenames


def test_load_documents_raises_on_empty_dir(tmp_path):
    try:
        load_documents(tmp_path)
        assert False, "Expected FileNotFoundError on empty directory"
    except FileNotFoundError:
        pass


def test_split_documents_produces_chunks():
    docs = load_documents(DOCS_DIR)
    chunks = split_documents(docs, chunk_size=300, chunk_overlap=50)
    assert len(chunks) >= len(docs), "Splitting should not reduce the number of chunks"
    for chunk in chunks:
        assert len(chunk.page_content) <= 400  # allow slack for separators


def test_load_and_split_end_to_end():
    chunks = load_and_split(DOCS_DIR)
    assert len(chunks) > 0
    assert all(chunk.metadata.get("source_file") for chunk in chunks)
