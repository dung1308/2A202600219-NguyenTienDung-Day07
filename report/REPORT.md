# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn TIến Dũng
**Nhóm:** Nhóm 61
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai vector trong không gian embedding có hướng gần giống nhau, thể hiện rằng hai đoạn văn bản đó có sự tương đồng về mặt ngữ nghĩa (semantic similarity) bất kể độ dài văn bản khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A:
- Sentence B:
- Tại sao tương đồng:
- Sentence A: "Python là một ngôn ngữ lập trình rất phổ biến trong lĩnh vực AI."
- Sentence B: "Ngôn ngữ Python được sử dụng rộng rãi để xây dựng các mô hình trí tuệ nhân tạo."
- Tại sao tương đồng: Cả hai đều nói về cùng một chủ đề (Python và AI) với ý nghĩa tương đương dù cách dùng từ khác nhau.

**Ví dụ LOW similarity:**
- Sentence A:
- Sentence B:
- Tại sao khác:
- Sentence A: "Ngày mai tôi đi mua sắm ở siêu thị."
- Sentence B: "Thuật toán sắp xếp nhanh (QuickSort) có độ phức tạp trung bình là O(n log n)."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác biệt (đời sống vs kỹ thuật máy tính).

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì Cosine Similarity tập trung vào góc giữa hai vector (hướng/ý nghĩa), trong khi Euclidean distance bị ảnh hưởng bởi độ dài (magnitude) của vector. Trong văn bản, một đoạn dài và một đoạn ngắn có thể cùng ý nghĩa nhưng vector của chúng sẽ rất xa nhau nếu đo bằng Euclidean.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*
> Phép tính: num_chunks = ceil((10,000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)
> Đáp án: 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Nếu overlap = 100, số chunk sẽ là ceil(9900 / 400) = 25 chunks (tăng lên). Chúng ta muốn overlap nhiều hơn để đảm bảo các thông tin quan trọng nằm ở ranh giới giữa các chunk không bị mất ngữ cảnh, giúp việc truy xuất (retrieval) chính xác hơn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Tài liệu kỹ thuật AI


**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain này vì tính thực tiễn cao, giúp cả nhóm hiểu sâu hơn về chính công nghệ đang học thông qua việc xây dựng một hệ thống "AI self-explaining". Dữ liệu kỹ thuật có cấu trúc phân cấp phức tạp (Markdown), là môi trường lý tưởng để so sánh sự khác biệt giữa các chiến thuật cắt nhỏ văn bản (Chunking) và đo lường độ chính xác của việc truy xuất các thuật ngữ chuyên môn.


### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | embed_ai.md | Product Case Studies | 3386 | domain: product, type: case_study |
| 2 | fast_api.md | Tech Tutorial | 56187 | domain: web_framework, type: documentation |
| 3 | hermes-agent...md | System Design | 14688 | domain: agent_backend, type: architecture |
| 4 | performance_guardrails...md | Quality Assurance | 3655 | domain: evaluation, type: infrastructure |
| 5 | rag_system_design.md | RAG Guide | 2416 | domain: rag, type: architecture |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| domain | string | rag, agent_backend, product | Giúp khu biệt không gian tìm kiếm. Ví dụ: Nếu hỏi về "pricing", hệ thống sẽ chỉ tìm trong domain agent_backend thay vì các tài liệu về web_framework |
| complexity | String | beginner, advanced | intermediate, advanced	Tăng trải nghiệm người dùng bằng cách cung cấp thông tin phù hợp với trình độ, tránh việc trả về các tài liệu quá chuyên sâu cho câu hỏi cơ bản. |


---


## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| RAG.md | FixedSizeChunker (`fixed_size`) | 272 | 199.6 | No (Splits mid-sentence) |
| RAG.md | SentenceChunker (`by_sentences`) | 91 | 594.7 | Yes (Keeps sentences whole) |
| RAG.md | RecursiveChunker (`recursive`) | 404 | 132.8 | Yes (Best structural balance) |
| hermes-agent-pricing-accuracy-architecture-design.md | FixedSizeChunker (`fixed_size`) | 74 | 198.5 | No (Splits mid-sentence) |
| hermes-agent-pricing-accuracy-architecture-design.md | SentenceChunker (`by_sentences`) | 30 | 487.7 | Yes (Keeps full sentences) |
| hermes-agent-pricing-accuracy-architecture-design.md | RecursiveChunker (`recursive`) | 102 | 142.2 | Yes (Respects structure) |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy] SentenceChunker

**Mô tả cách hoạt động:**
> Chiến lược này hoạt động bằng cách nhận diện các ranh giới câu thông qua các dấu kết thúc văn bản như `. `, `! `, `? ` hoặc `.\n`. Thay vì cắt văn bản dựa trên số lượng ký tự thô, nó phân tách nội dung thành các câu đơn lẻ và sau đó gom nhóm chúng lại thành từng khối (mặc định là 3 câu mỗi khối). Điều này đảm bảo mỗi đơn vị thông tin được lưu trữ luôn là một tập hợp các ý trọn vẹn, không bị mất đầu hoặc mất đuôi giữa chừng.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Các tài liệu trong domain của nhóm (như Case Study trong data hay kiến trúc hệ thống) thường chứa các phát biểu quan trọng hoặc các con số thống kê nằm trọn trong 1-2 câu. Việc sử dụng `SentenceChunker` giúp bảo toàn ngữ cảnh của các số liệu (như "tăng 20% ứng tuyển") đi kèm với nguyên nhân của nó trong cùng một khối, giúp Agent tránh được lỗi trích dẫn sai lệch khi tìm kiếm.

**Code snippet (nếu custom):**
```python
class TunedSentenceChunker:
    def __init__(self, max_sentences: int = 3):
        self.chunker = SentenceChunker(max_sentences_per_chunk=max_sentences)

    def chunk(self, text: str) -> list[str]:
        # Loại bỏ các khoảng trắng thừa trước khi chia để đảm bảo sentence boundary chuẩn hơn
        clean_text = " ".join(text.split())
        return self.chunker.chunk(clean_text)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| RAG.md | Recursive (Best Baseline) | 404 | 132.8 | High (Very granular) | +| RAG.md | Sentence (Của tôi) | 91 | 594.7 | Good (Context-rich) | +| hermes-agent...md | Recursive (Best Baseline) | 102 | 142.2 | High (Structure-aware) | +| hermes-agent...md | Sentence (Của tôi) | 30 | 487.7 | Excellent (Ideal for QA) |
| RAG.md | Recursive (Best Baseline) | 404 | 132.8 | High (Granular - Tốt cho tìm từ khóa) |
| RAG.md | **Sentence (Của tôi)** | 91 | 594.7 | Good (Context-rich - Tốt cho tóm tắt ý) |
| hermes-agent...md | Recursive (Best Baseline) | 102 | 142.2 | High (Structure-aware - Giữ đúng format code) |
| hermes-agent...md | **Sentence (Của tôi)** | 30 | 487.7 | Excellent (Ideal for QA - Tối ưu cho hỏi đáp logic) |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hieu | RecursiveChunker (`recursive`) | 8/10 | 102 chunks, avg 141.68; giữ cấu trúc tốt cho tài liệu dài | Tạo nhiều chunk hơn fixed-size nên top-k cần chọn hợp lý |
| Hải | RecursiveChunker2 (`recursive2`) | 8/10 | 103 chunks, avg 142.60; khá ổn định, giữ ngữ cảnh tốt | Cài đặt custom khó chuẩn hóa hơn strategy gốc |
| Nam | FixedSizeChunker (`fixed_size`) | 6/10 | 92 chunks, avg 199.22; đơn giản, ổn định, dễ triển khai | Dễ cắt giữa ý, giảm chất lượng ngữ cảnh |
| Dung | SentenceChunker (`by_sentences`) | 7/10 | 30 chunks, avg 487.73; giữ nguyên câu, dễ đọc | Chunk dài, dễ vượt mức kỳ vọng trên tài liệu nhiều câu |
| Duc Anh | Custom LLM-guided chunking | 8/10 | 44 chunks, avg 375.09; chọn được policy phù hợp cho tài liệu spec | Phụ thuộc vào prompt/LLM, khó tái lập nếu không chuẩn hóa |
| Vinh | SentenceChunker (`by_sentences`) | 7/10 | 30 chunks, avg 487.73; giữ nguyên câu, dễ đọc | Chunk dài, dễ vượt mức kỳ vọng trên tài liệu nhiều câu |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> LLM Chunk Classifier làm chiến thuật tốt nhất cho domain "Tài liệu kỹ thuật AI" là một hướng đi rất hiện đại và thông minh, nó có khả năng hiểu ngữ cảnh, "đọc" và hiểu bản chất của tài liệu, xử lý tài liệu phi cấu trúc và đa dạng, tối ưu hóa Metadata tự động và có cơ chế Fallback an toàn

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi sử dụng regex với kỹ thuật lookbehind `(?<=\. |! |\? |\.\n)` để chia văn bản tại các dấu kết thúc câu mà vẫn giữ lại được dấu câu đó. Sau đó, các câu được gom nhóm lại thành chuỗi sao cho số lượng câu trong mỗi chunk không vượt quá `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán duyệt qua danh sách separators ưu tiên cao (như \n\n) đến thấp (khoảng trắng). Nếu một đoạn văn vẫn lớn hơn `chunk_size`, hàm sẽ đệ quy xuống cấp độ separator tiếp theo. Base case là khi không còn separator nào thì cắt cứng theo độ dài.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Tài liệu được lưu trữ dưới dạng list các dictionary chứa embedding vector. Khi search, query được chuyển thành vector và tính Cosine Similarity với tất cả các record thông qua hàm `compute_similarity`, sau đó sắp xếp giảm dần theo điểm số.

**`search_with_filter` + `delete_document`** — approach:
> Tôi sử dụng kỹ thuật "Pre-filtering" - lọc danh sách record dựa trên metadata trước khi tính toán similarity để tối ưu hiệu năng. Hàm delete tìm và loại bỏ các bản ghi dựa trên `doc_id` được lưu trong metadata.

### KnowledgeBaseAgent

**`answer`** — approach:
> Agent lấy top-k chunks liên quan nhất từ store, gộp chúng lại thành một khối `context`. Sau đó, tôi xây dựng prompt bao gồm chỉ dẫn (Instruction) yêu cầu LLM chỉ trả lời dựa trên context, tiếp theo là phần context đã inject và câu hỏi của người dùng.

### Test Results

```
# Paste output of: pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.3, pluggy-1.6.0 -- e:\VinUNI_thuc_chien\lab_7\Day-07-Lab-Data-Foundations\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\VinUNI_thuc_chien\lab_7\Day-07-Lab-Data-Foundations
collected 42 items                                                             

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]
```


**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Indeed uses AI to improve job matching. | AI helps Indeed connect people to jobs faster. | high | 0.2423 | Yes |
| 2 | Recursive chunking splits by structural boundaries. | Paragraphs and newlines are used as separators in recursive splitting. |  low | -0.1048 | No |
| -0.1048 |
| 3 | Metadata helps filter relevant documents. | The weather in Hanoi is quite humid today. | low | | -0.0431 | No |
| 4 | Vector stores use cosine similarity. | Cosine similarity is the dot product divided by the product of magnitudes. | high | | 0.2067 | Yes |
| 5 | Klarna's AI assistant handles customer chats. | Human agents still resolve complex service issues at Klarna. | high | | 0.1574 | No |


**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là các cặp câu có ý nghĩa gần như trùng khớp (cặp 1, 2, 4) lại có điểm số rất thấp hoặc thậm chí âm. Điều này xảy ra vì `MockEmbedder` chỉ băm (hash) ký tự mà không hiểu ngữ nghĩa; để có kết quả chính xác phản ánh mối quan hệ giữa các khái niệm, chúng ta cần sử dụng các mô hình ngôn ngữ thực thụ như trong `LocalEmbedder`.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)


| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What does Hermes do to handle cache billing correctly? | It separates cache read and cache write tokens, normalizes usage before pricing, and uses route-aware official pricing sources. |
| 2 | What are the four layers in the high-level pricing architecture? | `usage_normalization`, `pricing_source_resolution`, `cost_estimation_and_reconciliation`, and `presentation`. |
| 3 | When should the UI show `included` instead of an estimated dollar amount? | When the billing route is subscription-included or explicitly marked as zero-cost/included, not when the cost is only estimated. |
| 4 | In the ML guide, what are the three main machine learning paradigms? | Supervised learning, unsupervised learning, and reinforcement learning. |
| 5 | In the FastHTML tutorial, what is HTMX used for? | HTMX is used to trigger requests from HTML elements and update parts of the page without reloading the entire page. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What does Hermes do to handle cache billing correctly? | Design Principles: Normalize usage, never fold cached tokens into input cost... | 0.224 | Yes | Hermes handles cache billing by normalizing usage and keeping cached tokens separate... |
| 2 | What are the four layers in the high-level pricing architecture? | High-Level Architecture: The system has four layers: usage_normalization, pricing_source_resolution... | 0.251 | Yes | The four layers are usage normalization, pricing source resolution, cost estimation, and presentation. |
| 3 | When should the UI show `included` instead of an estimated dollar amount? | Cost Status Model: 'included' status shows 'included' for subscription-backed routes. | 0.189 | Yes | Show 'included' for subscription or zero-cost routes instead of using estimates. |
| 4 | In the ML guide, what are the three main machine learning paradigms? | Types of ML: Categorized into Supervised, Unsupervised, and Reinforcement Learning. | 0.215 | Yes | The three main paradigms are supervised learning, unsupervised learning, and reinforcement learning. |
| 5 | In the FastHTML tutorial, what is HTMX used for? | HTMX extends HTML to allow triggering requests and updating parts of the page without refresh. | 0.198 | Yes | HTMX is used to trigger requests from any element and update page segments partially. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được từ các thành viên sử dụng RecursiveChunker cách tận dụng cấu trúc Markdown (Headers, Lists) để giữ các đoạn văn bản liên quan ở gần nhau hơn thay vì chỉ dựa vào ranh giới câu. Việc quan sát kết quả của nhóm giúp tôi hiểu rõ sự cân bằng giữa "độ chi tiết" (granularity) và "ngữ cảnh" (context window) trong việc tối ưu hóa retrieval.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Tôi ấn tượng với kỹ thuật Semantic Splitting (dùng LLM để phân loại chunk) từ nhóm bạn; kỹ thuật này giúp loại bỏ hoàn toàn việc cắt sai ý dù tài liệu có cấu trúc phức tạp đến đâu. Ngoài ra, việc bổ sung thêm Metadata "Summary" cho mỗi chunk giúp tăng tỷ lệ hit-rate khi người dùng đặt các câu hỏi mang tính chất tổng hợp thay vì hỏi dữ kiện cụ thể.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ chuyển sang chiến lược Hybrid: sử dụng Recursive để tách theo đoạn lớn nhưng đảm bảo ranh giới cuối cùng luôn là Sentence boundary để tránh vỡ câu. Bên cạnh đó, tôi sẽ đầu tư nhiều hơn vào việc làm sạch dữ liệu (Data Cleaning) để loại bỏ các ký tự thừa trong Markdown trước khi nhúng (embedding), giúp giảm nhiễu cho vector store.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5/ 5 |
| Document selection | Nhóm | 10/ 10 |
| Chunking strategy | Nhóm | 14/ 15 |
| My approach | Cá nhân | 9/ 10 |
| Similarity predictions | Cá nhân | 5/ 5 |
| Results | Cá nhân | 10/ 10 |
| Core implementation (tests) | Cá nhân | 30/ 30 |
| Demo | Nhóm | 3/ 5 |
| **Tổng** | | 86/ 100** |
(Tổng điểm tự đánh giá: 90)
