# 🤖 Autonomous AI Business Assistant

An end-to-end AI assistant designed to streamline enterprise document analysis, automate complex Q&A workflows, and generate structured business reports. Built using **LangChain**, **Python**, and **OpenAI APIs**, this project implements Retrieval-Augmented Generation (RAG) and Map-Reduce chains to answer context-aware queries over business documentation with precision.

---

## ✨ Features
* **Document Q&A (RAG Pipeline):** Query internal business documents with precise, context-aware answers.
* **Automated Summarization:** Uses Map-Reduce chains to summarize long-form reports and operational updates.
* **Report Generation:** Automatically generates formatted summary documents (`.docx`) based on query insights.
* **Modular Agent Architecture:** Easily extensible for adding new data sources and workflow tools.

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Framework:** LangChain
* **LLM Provider:** OpenAI API
* **Document Processing:** PyPDF / docx

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/jitendrameena177200-byte/autonomus-ai-business-assistant.git](https://github.com/jitendrameena177200-byte/autonomus-ai-business-assistant.git)
cd autonomus-ai-business-assistant
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
OPENAI_API_KEY=your_openai_api_key_here
python main.py ask "What were the Q3 sales risks?"
