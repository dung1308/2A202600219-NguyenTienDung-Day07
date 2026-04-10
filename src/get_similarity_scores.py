import os
import sys
from dotenv import load_dotenv

# Đảm bảo hệ thống tìm thấy package src
sys.path.append(os.getcwd())
load_dotenv()

from src.embeddings import OpenAIEmbedder
from src.chunking import compute_similarity

# Initialize OpenAI Embedder
embedder = OpenAIEmbedder()

# Define 5 Gold Pairs about AI Architecture
sentence_pairs = [
    {
        "pair": 1,
        "sentence_a": "The system uses vector embeddings for similarity search.",
        "sentence_b": "Vector embeddings are used by the system to perform similarity searches.",
        "prediction": "VERY HIGH - Active vs Passive voice of the same technical fact",
    },
    {
        "pair": 2,
        "sentence_a": "Retrieval-augmented generation improves LLM accuracy by providing context.",
        "sentence_b": "LLM responses are more accurate when context is provided via retrieval-augmented generation.",
        "prediction": "HIGH - Rephrased benefit of RAG without using acronyms",
    },
    {
        "pair": 3,
        "sentence_a": "FastHTML is a Python web framework for building AI applications.",
        "sentence_b": "The CEO of Indeed mentioned a 20% increase in job applications.",
        "prediction": "VERY LOW - Completely unrelated technical vs business facts",
    },
    {
        "pair": 4,
        "sentence_a": "Pricing accuracy is essential for building user trust.",
        "sentence_b": "User trust depends on accurate pricing information provided by the system.",
        "prediction": "HIGH - Semantic match between 'essential' and 'depends on'",
    },
    {
        "pair": 5,
        "sentence_a": "Performance guardrails ensure low latency in agent responses.",
        "sentence_b": "The technical documentation is stored in markdown files within the data directory.",
        "prediction": "VERY LOW - Infrastructure performance vs file storage organization",
    },
]

print("=" * 80)
print(f"COSINE SIMILARITY: OPENAI ({os.getenv('OPENAI_EMBEDDING_MODEL')})")
print("=" * 80)

for item in sentence_pairs:
    print(f"\nPair {item['pair']}:")
    # ... (giữ logic print cũ)
    
    # Compute actual similarity using OpenAI
    vec_a = embedder(item['sentence_a'])
    vec_b = embedder(item['sentence_b'])
    similarity = compute_similarity(vec_a, vec_b)
    
    print(f"  Actual Score: {similarity:.4f}")
    
    # Interpret the score
    if similarity > 0.9:
        interpretation = "VERY HIGH similarity"
    elif similarity > 0.7:
        interpretation = "HIGH similarity"
    elif similarity > 0.5:
        interpretation = "MODERATE similarity"
    elif similarity > 0.3:
        interpretation = "LOW similarity"
    else:
        interpretation = "VERY LOW similarity"
    
    print(f"  Interpretation: {interpretation}")

