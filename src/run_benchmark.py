import os
import sys
from dotenv import load_dotenv

# Đảm bảo hệ thống tìm thấy package src
sys.path.append(os.getcwd())
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

from src.embeddings import OpenAIEmbedder
from src.store import EmbeddingStore
from src.chunking import RecursiveChunker
from src.models import Document

def run_benchmark():
    # 1. Khởi tạo
    embedder = OpenAIEmbedder()
    store = EmbeddingStore(embedding_fn=embedder)
    chunker = RecursiveChunker(chunk_size=500)
    
    # 2. Xử lý tài liệu AI Architecture
    files = [
        "data/embed_ai.md",
        "data/fast_api.md",
        "data/hermes-agent-pricing-accuracy-architecture-design.md",
        "data/performance_guardrails_and_evaluation_architecture.md",
        "data/rag_system_design.md"
    ]
    
    print("--- Đang nạp dữ liệu vào Vector Store (AI Architecture) ---")
    all_chunks = []
    for f_path in files:
        if not os.path.exists(f_path): continue
        with open(f_path, "r", encoding="utf-8") as f:
            content = f.read()
            chunks = chunker.chunk(content)
            for i, chunk_text in enumerate(chunks):
                all_chunks.append(Document(
                    id=f"{os.path.basename(f_path)}_{i}",
                    content=chunk_text,
                    metadata={"source": f_path}
                ))
    
    store.add_documents(all_chunks)
    print(f"Đã nạp {len(all_chunks)} chunks.")
    
    # 3. Chạy 5 câu hỏi benchmark về AI Architecture
    queries = [
        # "Job application increase at Indeed?",
        # "How to install FastHTML?",
        # "Input tokens rule regarding cache?",
        # "Four main layers of Guardrails?",
        # "RAG failure behavior?"
        "What does Hermes do to handle cache billing correctly?",
        "What are the four layers in the high-level pricing architecture?",
        "When should the UI show `included` instead of an estimated dollar amount?",
        "In the ML guide, what are the three main machine learning paradigms?",
        "In the FastHTML tutorial, what is HTMX used for?"
    ]
    
    print("\n| # | Query | Top-1 Chunk (Preview) | Score |")
    print("|---|-------|----------------------|-------|")
    
    for i, q in enumerate(queries, 1):
        results = store.search(q, top_k=1)
        if results:
            res = results[0]
            # Lấy preview 100 ký tự đầu tiên
            preview = res['content'][:100].replace("\n", " ") + "..."
            print(f"| {i} | {q} | {preview} | {res['score']:.4f} |")

if __name__ == "__main__":
    run_benchmark()
