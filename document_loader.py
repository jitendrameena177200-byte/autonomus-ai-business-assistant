"""
document_loader.py
-------------------
Loads business documents (.txt, .pdf, .docx) from a directory, splits
them into chunks suitable for embedding, and attaches source metadata
so answers and summaries can be traced back to their origin document.
"""

from pathlib import Path
from typing import List

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


def _load_single_file(path: Path) -> List[Document]:
    """Pick the right LangChain loader based on file extension."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        loader = PyPDFLoader(str(path))
    elif suffix == ".docx":
        loader = Docx2txtLoader(str(path))
    else:  # .txt, .md, and other plain-text formats
        loader = TextLoader(str(path), encoding="utf-8")

    docs = loader.load()
    for doc in docs:
        doc.metadata["source_file"] = path.name
    return docs


def load_documents(documents_dir: Path) -> List[Document]:
    """Load every supported document in a directory (non-recursive by default)."""
    documents: List[Document] = []
    paths = sorted(p for p in documents_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS)

    if not paths:
        raise FileNotFoundError(
            f"No supported documents found in '{documents_dir}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    for path in paths:
        documents.extend(_load_single_file(path))

    return documents


def split_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> List[Document]:
    """Split loaded documents into overlapping chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def load_and_split(documents_dir: Path) -> List[Document]:
    """Convenience wrapper: load every file in a directory and chunk it."""
    return split_documents(load_documents(documents_dir))
