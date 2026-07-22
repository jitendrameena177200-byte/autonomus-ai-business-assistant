# Autonomous AI Business Assistant

An AI-powered assistant that answers business questions, summarizes internal
documents, and generates polished reports — built with **Python**,
**LangChain**, and the **OpenAI API**. Includes a working agentic workflow
layer that autonomously routes requests to the right tool (Q&A, summarization,
or report generation) and chains them together when a request needs more than
one step.

Sample data is modeled on a fictional company, **Trident Group**, so the
project runs end-to-end out of the box with realistic business documents
(sales reports, meeting minutes, HR policy, expense policy).

## Features

- **Document Q&A (RAG)** — ask natural-language questions and get answers
  grounded in your company's own documents, with source citations.
- **Automated summarization** — map-reduce summarization that scales to long
  documents without exceeding the LLM context window.
- **Report generation** — turns summaries or notes into a formatted `.docx`
  report with a title page, sections, and footer.
- **Agentic workflow automation** — a LangChain tool-calling agent that
  decides which capability to use (and in what order) for open-ended
  requests like *"Summarize the HR handbook and turn it into a report."*
- **CLI interface** — `ask`, `chat`, `summarize`, `summarize-all`, `report`,
  `agent`, and `reindex` commands.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for a full diagram and
design rationale.

```
src/
├── config.py            # Loads settings from .env
├── document_loader.py    # Loads + chunks .txt/.pdf/.docx documents
├── qa_engine.py          # RAG: Chroma vector store + retrieval QA chain
├── summarizer.py         # Map-reduce document summarization
├── report_generator.py   # Builds formatted .docx reports
└── agent_workflow.py     # Tool-calling agent that orchestrates everything
main.py                   # CLI entry point
data/documents/           # Sample Trident Group business documents
data/outputs/             # Generated reports land here
tests/                    # Pytest unit tests (no API key required)
```

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/autonomous-ai-business-assistant.git
cd autonomous-ai-business-assistant
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=sk-...
```

### 3. Run it

```bash
# Ask a question grounded in the sample Trident Group documents
python main.py ask "What were the key risks called out in the Q3 sales report?"

# Interactive chat
python main.py chat

# Summarize a single document
python main.py summarize quarterly_sales_report.txt

# Summarize every document in data/documents/
python main.py summarize-all

# Generate a formatted .docx report from all document summaries
python main.py report "Q3 FY2026 Board Summary"

# Let the autonomous agent decide how to handle a multi-step request
python main.py agent "Summarize the executive meeting minutes and the expense policy, then create a single report titled 'September Leadership Digest'"

# Rebuild the vector index after adding/editing documents
python main.py reindex
```

Generated reports are saved to `data/outputs/`.

## Example Output

```
$ python main.py ask "What is the parental leave policy?"

Trident Group provides 12 weeks of paid parental leave for the primary
caregiver and 6 weeks for the secondary caregiver, covering birth, adoption,
and foster placement. Leave must be taken within 12 months of the qualifying
event and can be split into two blocks with manager approval.
(Source: hr_handbook_excerpt.txt)

Sources: hr_handbook_excerpt.txt
```

## Adding Your Own Documents

Drop `.txt`, `.pdf`, or `.docx` files into `data/documents/`, then run:

```bash
python main.py reindex
```

The assistant will pick up the new content automatically for Q&A,
summarization, and reporting.

## Running Tests

```bash
pytest tests/ -v
```

Tests for document loading and configuration validation run without an
OpenAI API key. Tests that hit the live API are intentionally excluded to
keep CI free and deterministic — this is a common real-world pattern worth
knowing for interviews.

## Tech Stack

| Layer               | Tool                                  |
|---------------------|----------------------------------------|
| LLM & embeddings    | OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`) |
| Orchestration       | LangChain (RAG chains, tool-calling agent) |
| Vector store        | Chroma (persisted locally)             |
| Document generation | python-docx                            |
| CLI / UX            | argparse, rich                         |
| Config              | python-dotenv                          |

## Possible Extensions

- Swap Chroma for a hosted vector DB (Pinecone/Weaviate) for multi-user scale.
- Add a FastAPI wrapper to expose the assistant as a web API.
- Add Slack/Teams integration so the agent can respond in a channel.
- Add PDF report export alongside `.docx`.
- Add streaming responses for the CLI `chat` command.

## Disclaimer

Trident Group and all sample documents in `data/documents/` are fictional
and provided only to demonstrate the assistant end-to-end. Replace them with
your own (or your organization's) real documents before using this in
production.

## License

MIT — see [LICENSE](LICENSE).
