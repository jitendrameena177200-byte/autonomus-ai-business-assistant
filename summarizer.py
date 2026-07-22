"""
summarizer.py
-------------
Automated document summarization. Uses a map-reduce style prompt chain
so it scales to long documents without blowing past the LLM's context
window: each chunk is summarized individually, then the partial
summaries are combined into one final summary.
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import settings
from .document_loader import _load_single_file, split_documents

MAP_PROMPT = ChatPromptTemplate.from_template(
    "Summarize the key business points in this excerpt in 3-5 bullet points. "
    "Focus on facts, decisions, numbers, and action items. Ignore filler text.\n\n"
    "Excerpt:\n{chunk}"
)

REDUCE_PROMPT = ChatPromptTemplate.from_template(
    "You are writing an executive summary for {company_name}. Combine the "
    "following bullet-point notes (taken from different sections of the same "
    "document) into one coherent, non-repetitive summary of no more than "
    "{max_bullets} bullet points, followed by a one-sentence overall takeaway.\n\n"
    "Notes:\n{notes}"
)


class Summarizer:
    def __init__(self) -> None:
        settings.validate()
        self.llm = ChatOpenAI(
            model=settings.chat_model, api_key=settings.openai_api_key, temperature=0.3
        )
        self.map_chain = MAP_PROMPT | self.llm | StrOutputParser()
        self.reduce_chain = REDUCE_PROMPT | self.llm | StrOutputParser()

    def summarize_text(self, text: str, max_bullets: int = 6) -> str:
        """Summarize a raw block of text (used for ad-hoc pasted content)."""
        chunks = split_documents(
            [Document(page_content=text)],
            chunk_size=3000,
            chunk_overlap=200,
        )
        partial_summaries = [self.map_chain.invoke({"chunk": c.page_content}) for c in chunks]
        combined_notes = "\n".join(partial_summaries)
        return self.reduce_chain.invoke(
            {
                "notes": combined_notes,
                "company_name": settings.company_name,
                "max_bullets": max_bullets,
            }
        )

    def summarize_file(self, file_path: Path, max_bullets: int = 6) -> str:
        """Summarize a single document file (.txt, .pdf, .docx)."""
        docs = _load_single_file(file_path)
        chunks = split_documents(docs, chunk_size=3000, chunk_overlap=200)

        partial_summaries: List[str] = [
            self.map_chain.invoke({"chunk": chunk.page_content}) for chunk in chunks
        ]
        combined_notes = "\n".join(partial_summaries)

        final_summary = self.reduce_chain.invoke(
            {
                "notes": combined_notes,
                "company_name": settings.company_name,
                "max_bullets": max_bullets,
            }
        )
        return final_summary

    def summarize_directory(self, directory: Path) -> dict:
        """Summarize every supported document in a directory. Returns {filename: summary}."""
        from .document_loader import SUPPORTED_EXTENSIONS

        results = {}
        for path in sorted(directory.iterdir()):
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                results[path.name] = self.summarize_file(path)
        return results
