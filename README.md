# 🏢 RAG Chatbot for Company Documents

A premium, enterprise-grade Retrieval-Augmented Generation (RAG) chatbot that answers questions over company documents with citations, role-based access control, and an animated UI.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **Hybrid Retrieval**: Dense vector search + BM25 keyword search + cross-encoder reranking
- **Grounded Answers**: Every response cites source documents — no hallucinations
- **Section-Aware Chunking**: Smart document parsing that preserves context hierarchy
- **Role-Based Access**: Documents are filtered by user permissions before retrieval
- **Premium Animated UI**: Framer Motion-powered chat with staggered citation reveals
- **Source Drawer**: Click any citation to see the original document excerpt
- **Admin Dashboard**: Monitor ingestion status, document health, and retrieval metrics
- **100% Free Stack**: Uses Ollama (local LLM), ChromaDB, SQLite — no paid APIs

## 🏗️ Architecture

```
Next.js Frontend ←→ FastAPI Backend ←→ Ollama (LLM + Embeddings)
                                   ←→ ChromaDB (Vectors)
                                   ←→ SQLite (Users, Logs, Metadata)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running

### 1. Pull Ollama Models (Free)

```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

The API will be running at `http://localhost:8000`.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The UI will be running at `http://localhost:3000`.

### 4. Ingest Sample Documents

Upload the sample HR documents from `sample_data/` via the admin dashboard or the API:

```bash
curl -X POST http://localhost:8000/api/documents/ingest-sample
```

## 📁 Project Structure

```
├── frontend/          # Next.js 14 + Tailwind + Framer Motion
├── backend/           # FastAPI + LlamaIndex + ChromaDB
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic (ingestion, retrieval, generation)
│   │   └── utils/     # Chunking, citations, helpers
│   └── data/          # Uploads, ChromaDB storage, sample docs
├── sample_data/       # Sample HR policy documents
└── docs/              # PRD, tech design, workflow docs
```

## 🧪 Pilot Use Case: HR Policy & Onboarding

The initial deployment targets HR policy Q&A with sample documents covering:
- Employee Handbook
- Leave Policy
- Onboarding Guide
- Benefits Overview
- Code of Conduct

## 📝 License

MIT
