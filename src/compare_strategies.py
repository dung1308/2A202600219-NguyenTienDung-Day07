import os
import sys
import re

# Đảm bảo hệ thống tìm thấy package src
sys.path.append(os.getcwd())

# Cấu hình encoding cho Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.chunking import ChunkingStrategyComparator

def calculate_boundary_score(chunks: list[str]) -> float:
    """
    Tính điểm 'Boundary Cleanliness': Tỉ lệ ranh giới kết thúc bằng dấu câu hoặc xuống dòng.
    """
    if not chunks:
        return 0.0
    
    # Chúng ta kiểm tra ranh giới giữa các chunk (bỏ qua chunk cuối cùng vì nó kết thúc văn bản)
    count = 0
    valid_boundaries = 0
    
    # Dấu hiệu ngắt câu/đoạn tự nhiên
    pattern = r'[.!?\n]\s*$'
    
    for i in range(len(chunks) - 1):
        count += 1
        if re.search(pattern, chunks[i]):
            valid_boundaries += 1
            
    return (valid_boundaries / count * 100) if count > 0 else 100.0

def main():
    comparator = ChunkingStrategyComparator()
    
    # List of 5 AI Architecture & Design documents
    files = [
        "data/embed_ai.md",
        "data/fast_api.md",
        "data/hermes-agent-pricing-accuracy-architecture-design.md",
        "data/performance_guardrails_and_evaluation_architecture.md",
        "data/rag_system_design.md"
    ]
    
    all_results = []
    
    # --- BƯỚC 1: THU THẬP DỮ LIỆU ---
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        results = comparator.compare(text, chunk_size=300)
        file_name = os.path.basename(file_path)
        
        file_data = {"name": file_name, "strategies": []}
        
        for strategy_key in ["fixed_size", "by_sentences", "recursive"]:
            stats = results[strategy_key]
            boundary_score = calculate_boundary_score(stats['chunks'])
            file_data["strategies"].append({
                "key": strategy_key,
                "name": strategy_key.replace('_', ' ').title().replace(' ', ''),
                "stats": stats,
                "boundary_score": boundary_score
            })
        all_results.append(file_data)

    print("\n" + "="*95)
    print(" BÁO CÁO TỔNG HỢP CHUNKING STRATEGIES (Dùng cho REPORT.md mục 3.1)")
    print("="*95 + "\n")
    
    # --- BƯỚC 2: IN BẢNG THỐNG KÊ TỔNG HỢP ---
    print("| Tài liệu | Strategy | Count | Avg Len | Boundary Score |")
    print("|-----------|----------|-------|---------|----------------|")
    for doc in all_results:
        for strat in doc["strategies"]:
            name = strat["name"] + "Chunker"
            print(f"| {doc['name']:<28} | {name:<17} | {strat['stats']['count']:<5} | {strat['stats']['avg_length']:<7.1f} | {strat['boundary_score']:>13.1f}% |")

    # --- BƯỚC 3: IN CHI TIẾT PREVIEW ---
    print("\n\n" + "="*95)
    print(" CHI TIẾT PREVIEW: TOP 3 CHUNKS")
    print("="*95)
    
    for doc in all_results:
        print(f"\n>>> TÀI LIỆU: {doc['name']}")
        print("-" * 50)
        for strat in doc["strategies"]:
            print(f"   [Chiến lược: {strat['name']}]")
            for i, chunk in enumerate(strat['stats']['chunks'][:3], 1):
                preview = chunk.replace('\n', ' ').strip()[:110]
                print(f"     Chunk {i}: {preview}...")
            print()

    print("="*95 + "\n")

if __name__ == "__main__":
    main()
