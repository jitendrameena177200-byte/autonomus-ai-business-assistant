"""
qa_engine.py
------------
Retrieval-Augmented Generation (RAG) engine. Embeds business documents
into a Chroma vector store and answers natural-language questions by
retrieving the most relevant chunks and passing them to an LLM.
"""

from pathlib import Path
from typing import List, Tuple

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import settings
from .document_loader import load_and_split

QA_SYSTEM_PROMPT = """You are the Autonomous AI Business Assistant for {company_name}.
Answer the user's question using ONLY the context below, which was retrieved
from the company's internal documents. If the answer isn't in the context,
say you don't have enough information rather than guessing.

Always be concise, professional, and cite the source file(s) you used at the
end of your answer in the format: (Source: filename.ext)

Context:
{context}
"""


def _format_docs(docs: List[Document]) -> str:
    return "\n\n---\n\n".join(
        f"[{doc.metadata.get('source_file', 'unknown')}]\n{doc.page_content}" for doc in docs
    )


class QAEngine:
    """Builds/loads a vector store and answers questions over it."""

    def __init__(self) -> None:
        settings.validate()
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model, api_key=settings.openai_api_key
        )
        self.llm = ChatOpenAI(
            model=settings.chat_model, api_key=settings.openai_api_key, temperature=0.2
        )
        self.vectorstore = self._load_or_build_vectorstore()
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        self.chain = self._build_chain()

    def _load_or_build_vectorstore(self) -> Chroma:
        persist_dir = str(settings.vector_store_dir)
        vectorstore = Chroma(
            collection_name="business_documents",
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
        )
        # If empty, populate it from the documents directory.
        if vectorstore._collection.count() == 0:
            chunks = load_and_split(settings.documents_dir)
            vectorstore.add_documents(chunks)
        return vectorstore

    def rebuild_index(self) -> int:
        """Force a fresh rebuild of the vector store from source documents."""
        chunks = load_and_split(settings.documents_dir)
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name="business_documents",
            persist_directory=str(settings.vector_store_dir),
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        self.chain = self._build_chain()
        return len(chunks)

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", QA_SYSTEM_PROMPT),
                ("human", "{question}"),
            ]
        )

        def build_inputs(question: str):
            docs = self.retriever.invoke(question)
            return {
                "context": _format_docs(docs),
                "question": question,
                "company_name": settings.company_name,
            }

        return (
            RunnablePassthrough().pick("question")
            | (lambda x: build_inputs(x["question"]) if isinstance(x, dict) else build_inputs(x))
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> Tuple[str, List[str]]:
        """Answer a question and return (answer, list_of_source_files)."""
        docs = self.retriever.invoke(question)
        sources = sorted({doc.metadata.get("source_file", "unknown") for doc in docs})
        answer = self.chain.invoke({"question": question})
        return answer, sources
