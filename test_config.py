"""
Unit tests for config.py. Verifies that missing/placeholder API keys
are caught early with a clear error, instead of failing deep inside
a LangChain call.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import Settings


def test_validate_raises_on_placeholder_key(tmp_path):
    settings = Settings(
        openai_api_key="sk-your-key-here",
        chat_model="gpt-4o-mini",
        embedding_model="text-embedding-3-small",
        documents_dir=tmp_path / "documents",
        output_dir=tmp_path / "outputs",
        vector_store_dir=tmp_path / "vector_store",
        company_name="Trident Group",
    )
    with pytest.raises(EnvironmentError):
        settings.validate()


def test_validate_passes_with_real_looking_key(tmp_path):
    settings = Settings(
        openai_api_key="sk-abc123-real-looking-key",
        chat_model="gpt-4o-mini",
        embedding_model="text-embedding-3-small",
        documents_dir=tmp_path / "documents",
        output_dir=tmp_path / "outputs",
        vector_store_dir=tmp_path / "vector_store",
        company_name="Trident Group",
    )
    settings.validate()  # should not raise
    assert settings.documents_dir.exists()
    assert settings.output_dir.exists()
    assert settings.vector_store_dir.exists()
