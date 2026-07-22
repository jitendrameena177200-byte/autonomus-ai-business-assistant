"""
config.py
---------
Central configuration for the Autonomous AI Business Assistant.
Loads settings from environment variables (via .env) so no secrets
are ever hard-coded into the source.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present.
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    chat_model: str
    embedding_model: str
    documents_dir: Path
    output_dir: Path
    vector_store_dir: Path
    company_name: str

    def validate(self) -> None:
        """Raise a clear error early if required config is missing."""
        if not self.openai_api_key or self.openai_api_key.startswith("sk-your"):
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and add "
                "your real OpenAI API key before running the assistant."
            )
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        documents_dir=PROJECT_ROOT / os.getenv("DOCUMENTS_DIR", "data/documents"),
        output_dir=PROJECT_ROOT / os.getenv("OUTPUT_DIR", "data/outputs"),
        vector_store_dir=PROJECT_ROOT / os.getenv("VECTOR_STORE_DIR", "data/vector_store"),
        company_name=os.getenv("COMPANY_NAME", "Trident Group"),
    )


settings = get_settings()
