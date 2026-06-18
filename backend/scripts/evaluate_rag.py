import os
import json
import asyncio
import httpx
import pandas as pd
from datasets import Dataset

# Langchain and RAGAS imports
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
)

# Configuration
API_URL = "http://localhost:8000/api/chat/query"
OLLAMA_URL = "http://localhost:11434"

# 1. Define Gold-Standard Test Set (HR Policy Q&A)
# We won't strictly need `ground_truth` for these three metrics, but we define typical questions
TEST_QUERIES = [
    "What is the company's policy on remote work?",
    "How many paid time off (PTO) days do new employees get?",
    "What should I do if I am sick and cannot work?",
    "What is the code of conduct regarding gifts from vendors?",
    "Does the company offer a 401k match?",
]

async def fetch_rag_response(query: str):
    """Hits the local FastAPI backend to get the generated answer and retrieved contexts."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                API_URL,
                json={"query": query, "session_id": None, "department_filter": "HR"},
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            # The backend returns citations. We need to extract the raw text excerpts as 'contexts' for RAGAS.
            answer = data.get("answer", "")
            citations = data.get("citations", [])
            contexts = [c.get("excerpt", "") for c in citations]
            
            return {
                "question": query,
                "answer": answer,
                "contexts": contexts,
                # context_precision requires ground_truth if we were doing recall, but let's provide a dummy ground_truth or omit it if possible. 
                # Newer RAGAS might strictly require ground_truth for some metrics. If it fails, we will remove context_precision.
            }
        except Exception as e:
            print(f"Error fetching response for '{query}': {e}")
            return None

async def main():
    print("🚀 Starting Automated RAG Evaluation...")
    print("Collecting answers and contexts from the backend...")
    
    data_samples = {
        "question": [],
        "answer": [],
        "contexts": [],
    }
    
    for query in TEST_QUERIES:
        print(f"  -> Querying: {query}")
        result = await fetch_rag_response(query)
        if result and result["answer"]:
            data_samples["question"].append(result["question"])
            data_samples["answer"].append(result["answer"])
            data_samples["contexts"].append(result["contexts"])
            
    if not data_samples["question"]:
        print("❌ No valid responses received from backend. Is the server running?")
        return

    # Create HuggingFace Dataset
    dataset = Dataset.from_dict(data_samples)
    
    print("\n📦 Initializing RAGAS with local Ollama models...")
    # Initialize Local Evaluator LLM and Embeddings
    # We use llama3.2 for the judge and nomic-embed-text for embedding similarity metrics
    chat_model = ChatOllama(model="llama3.2", base_url=OLLAMA_URL, temperature=0.0)
    emb_model = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)
    
    try:
        evaluator_llm = LangchainLLMWrapper(chat_model)
        evaluator_embeddings = LangchainEmbeddingsWrapper(emb_model)
        
        # Override metric models
        for m in [faithfulness, answer_relevancy, context_precision]:
            if hasattr(m, "llm"):
                m.llm = evaluator_llm
            if hasattr(m, "embeddings"):
                m.embeddings = evaluator_embeddings

        print("\n⏳ Running RAGAS Evaluation (this may take a few minutes)...")
        # Note: context_precision generally requires 'ground_truth'. We will try without it first. 
        # If it fails, we'll run just faithfulness and answer_relevancy which are reference-free.
        metrics = [faithfulness, answer_relevancy]
        
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
            raise_exceptions=False,
        )
        
        df = result.to_pandas()
        
        # Save Report
        os.makedirs("data", exist_ok=True)
        report_path = "data/evaluation_report.csv"
        df.to_csv(report_path, index=False)
        
        print("\n✅ Evaluation Complete!")
        print("-" * 50)
        print(f"Faithfulness Score:   {result.get('faithfulness', 'N/A'):.4f}")
        print(f"Answer Relevancy:     {result.get('answer_relevancy', 'N/A'):.4f}")
        print("-" * 50)
        print(f"Detailed report saved to: {report_path}")
        
    except Exception as e:
        print(f"\n❌ Evaluation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
