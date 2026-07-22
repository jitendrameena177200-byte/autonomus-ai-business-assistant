# Architecture

```
                         ┌─────────────────────────┐
                         │       main.py (CLI)      │
                         └────────────┬─────────────┘
                                      │
        ┌─────────────────┬──────────┼───────────────┬────────────────┐
        ▼                 ▼          ▼                ▼                ▼
 ┌─────────────┐   ┌─────────────┐ ┌───────────┐ ┌─────────────┐ ┌────────────┐
 │ document_    │   │ qa_engine.py│ │summarizer │ │report_      │ │agent_      │
 │ loader.py    │◄──┤ (RAG)       │ │.py        │ │generator.py │ │workflow.py │
 └─────────────┘   └─────────────┘ └───────────┘ └─────────────┘ └─────┬──────┘
        ▲                 ▲              ▲               ▲             │
        │                 │              │               │             │
        └─────────────────┴──────────────┴───────────────┴─────────────┘
                     all four modules are exposed as tools to the
                     LangChain tool-calling agent in agent_workflow.py

 Data flow for Q&A:
   documents/*.txt,.pdf,.docx --> document_loader (load+chunk)
      --> OpenAI Embeddings --> Chroma vector store (persisted on disk)
      --> similarity search (top-k) --> ChatOpenAI --> grounded answer + sources

 Data flow for summarization:
   single document --> chunk --> map (per-chunk bullet summary)
      --> reduce (combine into executive summary)

 Data flow for reporting:
   section notes (from summarizer or user) --> LLM expands into prose
      --> python-docx assembles title page + sections --> .docx saved to data/outputs/

 Data flow for the agent:
   free-form user request --> tool-calling LLM agent decides which of
      {answer_question, summarize_document, create_report, list_available_documents}
      to call, in what order, chaining outputs between steps automatically.
```

## Why this design

- **RAG over fine-tuning**: business documents change constantly (new
  reports, updated policies). Re-embedding a changed document is cheap;
  fine-tuning is not. RAG also gives traceable citations, which matters
  for business trust.
- **Map-reduce summarization**: keeps the design correct for documents
  longer than a single context window, and is easy to explain/defend
  in an interview.
- **Separate report generator**: decouples "understanding content" from
  "producing a deliverable," so the same summaries can feed a report,
  a chat answer, or a Slack message without duplicating logic.
- **Tool-calling agent as the outer layer**: this is what makes the
  assistant "autonomous" rather than a fixed pipeline - it decides which
  capability to invoke based on the request.
