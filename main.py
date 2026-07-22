#!/usr/bin/env python3
"""
main.py
-------
Command-line interface for the Autonomous AI Business Assistant.

Usage:
    python main.py ask "What was our Q3 revenue growth?"
    python main.py summarize quarterly_sales_report.txt
    python main.py summarize-all
    python main.py report "Q3 Board Summary"
    python main.py agent "Summarize the HR handbook and email-ready report"
    python main.py reindex
    python main.py chat
"""

import argparse
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agent_workflow import build_agent, run_agent
from src.config import settings
from src.qa_engine import QAEngine
from src.report_generator import ReportGenerator
from src.summarizer import Summarizer

console = Console()


def cmd_ask(args):
    engine = QAEngine()
    answer, sources = engine.ask(args.question)
    console.print(Panel(Markdown(answer), title="Answer", border_style="cyan"))
    console.print(f"[dim]Sources: {', '.join(sources)}[/dim]")


def cmd_chat(_args):
    engine = QAEngine()
    console.print(
        Panel(
            f"Chatting with the {settings.company_name} Business Assistant. "
            "Type 'exit' to quit.",
            border_style="green",
        )
    )
    while True:
        question = console.input("[bold cyan]You:[/bold cyan] ")
        if question.strip().lower() in {"exit", "quit"}:
            break
        answer, sources = engine.ask(question)
        console.print(f"[bold green]Assistant:[/bold green] {answer}")
        console.print(f"[dim]Sources: {', '.join(sources)}[/dim]\n")


def cmd_summarize(args):
    summarizer = Summarizer()
    path = settings.documents_dir / args.filename
    if not path.exists():
        console.print(f"[red]File not found:[/red] {path}")
        sys.exit(1)
    summary = summarizer.summarize_file(path)
    console.print(Panel(Markdown(summary), title=f"Summary: {args.filename}", border_style="magenta"))


def cmd_summarize_all(_args):
    summarizer = Summarizer()
    results = summarizer.summarize_directory(settings.documents_dir)
    for filename, summary in results.items():
        console.print(Panel(Markdown(summary), title=f"Summary: {filename}", border_style="magenta"))


def cmd_report(args):
    summarizer = Summarizer()
    generator = ReportGenerator()
    console.print("[yellow]Summarizing all source documents...[/yellow]")
    summaries = summarizer.summarize_directory(settings.documents_dir)
    sections = {f"Summary - {name}": summary for name, summary in summaries.items()}
    path = generator.generate_report(title=args.title, sections=sections, expand_with_llm=False)
    console.print(f"[green]Report saved to:[/green] {path}")


def cmd_agent(args):
    executor = build_agent()
    output = run_agent(args.request, executor)
    console.print(Panel(Markdown(output), title="Agent Result", border_style="blue"))


def cmd_reindex(_args):
    engine = QAEngine()
    count = engine.rebuild_index()
    console.print(f"[green]Rebuilt vector index with {count} chunks.[/green]")


def main():
    parser = argparse.ArgumentParser(description="Autonomous AI Business Assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ask = sub.add_parser("ask", help="Ask a one-off question over the documents")
    p_ask.add_argument("question")
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="Interactive Q&A chat loop")
    p_chat.set_defaults(func=cmd_chat)

    p_sum = sub.add_parser("summarize", help="Summarize a single document by filename")
    p_sum.add_argument("filename")
    p_sum.set_defaults(func=cmd_summarize)

    p_sum_all = sub.add_parser("summarize-all", help="Summarize every document in the documents dir")
    p_sum_all.set_defaults(func=cmd_summarize_all)

    p_report = sub.add_parser("report", help="Generate a .docx report from all document summaries")
    p_report.add_argument("title")
    p_report.set_defaults(func=cmd_report)

    p_agent = sub.add_parser("agent", help="Give the autonomous agent a free-form request")
    p_agent.add_argument("request")
    p_agent.set_defaults(func=cmd_agent)

    p_reindex = sub.add_parser("reindex", help="Rebuild the vector store from source documents")
    p_reindex.set_defaults(func=cmd_reindex)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
