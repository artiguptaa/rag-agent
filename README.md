# GitHub RAG Chat

A Streamlit application that ingests a GitHub repository, creates a vector index with LlamaIndex, and answers questions about the repository using retrieval-augmented generation.

## Features

- GitHub repository ingestion with `gitingest`
- Markdown document parsing
- Hugging Face embeddings with `BAAI/bge-large-en-v1.5`
- Groq-powered responses through LlamaIndex
- Streaming assistant responses in the Streamlit interface
- Progress updates while parsing, embedding, and indexing
- Session-level caching for loaded repositories and models

## Requirements

- Python 3.9 or newer
- A Groq API key

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r .\requitements.txt
```

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key
```

`OPENAI_API_KEY` is also accepted as a fallback for the Groq client, but `GROQ_API_KEY` is recommended.

## Run

```powershell
streamlit run .\app.py
```

Streamlit automatically reloads the application when Python source files change during development.

## Project Structure

```text
app.py                  Application entry point
streamlit_app.py        Streamlit UI and workflow coordinator
app_state.py            Session state management
repository_service.py   GitHub ingestion and document loading
rag_engine.py           LLM, embeddings, indexing, and query engine
response_streamer.py    Async streaming adapter for LlamaIndex responses
requitements.txt        Python dependencies
```

## Usage

1. Start the application.
2. Enter a public GitHub repository URL in the sidebar.
3. Select **Load Repository**.
4. Wait for parsing, embedding, and indexing to complete.
5. Ask questions about the repository in the chat box.

The `.env` file and generated `content.md` file are excluded from version control.