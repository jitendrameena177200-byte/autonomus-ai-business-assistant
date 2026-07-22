"""
agent_workflow.py
------------------
The "autonomous" layer of the assistant. Wraps the Q&A engine,
summarizer, and report generator as LangChain tools and lets an LLM
agent decide which tool(s) to call to satisfy a natural-language
request, e.g.:

  "Summarize the Q3 sales report and turn it into a one-page report."

This demonstrates tool-calling / agentic workflow automation rather
than a single fixed pipeline.
"""

from pathlib import Path
from typing import List, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from .config import settings
from .qa_engine import QAEngine
from .report_generator import ReportGenerator
from .summarizer import Summarizer

AGENT_SYSTEM_PROMPT = f"""You are the Autonomous AI Business Assistant for {settings.company_name}.
You have access to tools for answering questions about internal documents,
summarizing documents, and generating polished .docx business reports.

Guidelines:
- Use `answer_question` for factual questions about company documents.
- Use `summarize_document` when the user wants a shorter version of a specific file.
- Use `create_report` when the user wants a formatted deliverable document.
- Chain tools together when a request needs multiple steps (e.g. summarize
  several files, then compile them into one report).
- Always tell the user what you did and where any generated file was saved.
"""


def build_agent(
    qa_engine: Optional[QAEngine] = None,
    summarizer: Optional[Summarizer] = None,
    report_generator: Optional[ReportGenerator] = None,
) -> AgentExecutor:
    settings.validate()
    qa_engine = qa_engine or QAEngine()
    summarizer = summarizer or Summarizer()
    report_generator = report_generator or ReportGenerator()

    @tool
    def answer_question(question: str) -> str:
        """Answer a natural-language question using the company's internal documents (RAG)."""
        answer, sources = qa_engine.ask(question)
        return f"{answer}\n\nSources: {', '.join(sources)}"

    @tool
    def summarize_document(filename: str) -> str:
        """Summarize a single document by filename (must exist in the documents directory)."""
        path = settings.documents_dir / filename
        if not path.exists():
            return f"Error: '{filename}' was not found in {settings.documents_dir}."
        return summarizer.summarize_file(path)

    @tool
    def list_available_documents() -> str:
        """List the filenames of all documents currently available to the assistant."""
        from .document_loader import SUPPORTED_EXTENSIONS

        files = [p.name for p in settings.documents_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS]
        return ", ".join(sorted(files)) if files else "No documents found."

    @tool
    def create_report(title: str, section_titles_and_notes: str) -> str:
        """
        Create a formatted .docx business report.
        `section_titles_and_notes` must be formatted as:
        'Section One:: notes for section one || Section Two:: notes for section two'
        Use '::' to separate a section title from its notes, and '||' between sections.
        """
        sections = {}
        for chunk in section_titles_and_notes.split("||"):
            if "::" in chunk:
                heading, notes = chunk.split("::", 1)
                sections[heading.strip()] = notes.strip()
        if not sections:
            return "Error: could not parse any sections. Use 'Heading:: notes || Heading2:: notes2' format."
        path = report_generator.generate_report(title=title, sections=sections)
        return f"Report created at: {path}"

    tools = [answer_question, summarize_document, list_available_documents, create_report]

    llm = ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key, temperature=0.2)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", AGENT_SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=8)


def run_agent(request: str, executor: Optional[AgentExecutor] = None) -> str:
    executor = executor or build_agent()
    result = executor.invoke({"input": request})
    return result["output"]
