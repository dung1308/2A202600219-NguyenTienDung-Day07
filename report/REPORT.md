# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Trần Long Hải]
**Nhóm:** [Tên nhóm]
**Ngày:** [10/04/2026]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Cosine similarity đo lường góc giữa hai vector trong không gian. Giá trị cao (gần 1) có nghĩa là hai vector hướng về cùng một phía, biểu thị rằng hai đoạn văn bản có sự tương đồng lớn về mặt ngữ nghĩa, mặc dù từ ngữ có thể khác nhau.*

**Ví dụ HIGH similarity:**
- Sentence A: "Tôi rất thích ăn táo."
- Sentence B: "Táo là loại trái cây mà tôi ưa chuộng nhất."
- Tại sao tương đồng: Cả hai đều diễn đạt cùng một sở thích về táo, dù sử dụng từ vựng khác nhau ("thích ăn" vs "ưa chuộng nhất").

**Ví dụ LOW similarity:**
- Sentence A: "Hôm nay trời nắng đẹp."
- Sentence B: "Cổ phiếu VinFast đang tăng giá."
- Tại sao khác: Một câu nói về thời tiết, một câu nói về kinh tế/tài chính, không có mối liên hệ ngữ nghĩa nào.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Vì Cosine similarity tập trung vào hướng của vector thay vì độ dài (magnitude). Trong văn bản, một từ có thể lặp lại nhiều lần làm tăng độ dài vector nhưng không thay đổi ngữ nghĩa chính; Cosine similarity loại bỏ được ảnh hưởng của độ dài văn bản này.*

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Phép tính: num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)*
> *Đáp án: 23 chunks*

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Chunk count sẽ tăng lên (ceil(9900/400) = 25 chunks). Chúng ta muốn overlap nhiều hơn để đảm bảo các thông tin quan trọng ở ranh giới giữa hai chunk không bị mất context, giúp LLM hiểu được mối liên kết giữa các đoạn.*

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** AI Architecture & Advanced System Design (Kiến trúc và Thiết kế hệ thống AI nâng cao).

**Tại sao nhóm chọn domain này?**
> *Chúng tôi chọn domain này vì đây là lĩnh vực có độ phức tạp kỹ thuật cao, yêu cầu độ chính xác tuyệt đối trong việc truy xuất các thông số (ví dụ: tỷ lệ %, câu lệnh cài đặt, các lớp kiến trúc). Dữ liệu bao gồm cả hướng dẫn lập trình, thiết kế hệ thống và báo cáo kinh doanh, giúp kiểm chứng khả năng xử lý đa dạng của RAG Agent.*

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
| domain | string | evaluation, product | Giúp giới hạn phạm vi tìm kiếm khi người dùng hỏi về một mảng cụ thể như "Evaluation". |
| type | string | architecture, documentation | Phân loại tài liệu theo tính chất (thiết kế vs hướng dẫn sử dụng) để ưu tiên nguồn tin cậy. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` (`compare_strategies.py`) trên 5 tài liệu AI (chunk_size=300):

| Tài liệu | Strategy | Count | Avg Len | Boundary Score |
|-----------|----------|-------|---------|----------------|
| rag_system_design.md         | FixedSizeChunker  | 10    | 284.1   |           0.0% |
| rag_system_design.md         | BySentencesChunker | 5     | 476.0   |         100.0% |
| rag_system_design.md         | RecursiveChunker  | 18    | 132.8   |         100.0% |
| fast_api.md                  | RecursiveChunker  | 200+  | ~250    |         100.0% |

#### First 3 Chunks Preview (hermes-agent-pricing-accuracy-architecture-design.md)

**1. FixedSizeChunker:**
- *Chunk 1:* "# Pricing Accuracy Architecture  Date: 2026-03-16  ## Goal  Hermes should only show dollar costs when they are..."
- *Chunk 2:* "un_agent.py` - `agent/usage_pricing.py` - `agent/insights.py` - `cli.py`  with a provider-aware pricing system..."
- *Chunk 3:* "n providers expose authoritative billing data - supports direct providers, OpenRouter, subscriptions, enterpri.."

**2. SentenceChunker:**
- *Chunk 1:* "# Pricing Accuracy Architecture  Date: 2026-03-16  ## Goal  Hermes should only show dollar costs when they are..."
- *Chunk 2:* "2. It uses a static model price table and fuzzy heuristics, which can drift from current official pricing. 3...."
- *Chunk 3:* "It assumes public API list pricing matches the user's real billing path. 4. It has no distinction between live..."

**3. RecursiveChunker:**
- *Chunk 1:* "# Pricing Accuracy Architecture  Date: 2026-03-16  ## Goal  Hermes should only show dollar costs when they are..."
- *Chunk 2:* "- `run_agent.py` - `agent/usage_pricing.py` - `agent/insights.py` - `cli.py`  with a provider-aware pricing sy..."
- *Chunk 3:* "- handles cache billing correctly - distinguishes `actual` vs `estimated` vs `included` vs `unknown` - reconci..."

### Strategy Của Tôi

**Loại:** `FixedSizeChunker`, `SentenceChunker`, `RecursiveChunker`

**Mô tả cách hoạt động:**
> *Hệ thống triển khai 3 cấp độ chunking khác nhau: (1) **FixedSizeChunker** thực hiện cắt văn bản theo số lượng ký tự cố định, đơn giản nhưng dễ ngắt quãng thông tin. (2) **SentenceChunker** sử dụng regex để ngắt tại ranh giới câu, đảm bảo mạch câu được giữ nguyên. (3) **RecursiveChunker** thực hiện chia nhỏ theo các đoạn văn bản (\n\n, \n, khoảng trắng) để giữ cấu trúc phân tầng tự nhiên của tài liệu cho đến khi đạt kích thước mục tiêu.*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Domain AI Architecture chứa nhiều khối code, danh sách gạch đầu dòng và phân cấp tiêu đề Markdown chặt chẽ. Việc kết hợp 3 chiến lược này, đặc biệt là Recursive, giúp bảo toàn tính toàn vẹn của các cấu trúc dữ liệu kỹ thuật, đảm bảo mã nguồn và các bước quy trình không bị cắt rời mảnh vụn.*

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| embed_ai.md                  | FixedSizeChunker (Baseline)  | 13    | 298.9   |           0.0% |
| embed_ai.md                  | BySentencesChunker | 9     | 363.0   |         100.0% |
| embed_ai.md                  | RecursiveChunker  | 17    | 193.3   |         100.0% |
| fast_api.md                  | FixedSizeChunker (Baseline)  | 217   | 300.0   |           5.6% |
| fast_api.md                  | BySentencesChunker | 95    | 569.5   |         100.0% |
| fast_api.md                  | RecursiveChunker  | 259   | 209.6   |         100.0% |
| hermes-agent-pricing-accuracy-architecture-design.md | FixedSizeChunker (Baseline)  | 59    | 298.1   |           8.6% |
| hermes-agent-pricing-accuracy-architecture-design.md | BySentencesChunker | 30    | 487.7   |         100.0% |
| hermes-agent-pricing-accuracy-architecture-design.md | RecursiveChunker  | 64    | 229.5   |         100.0% |
| performance_guardrails_and_evaluation_architecture.md | FixedSizeChunker (Baseline)  | 12    | 296.5   |           0.0% |
| performance_guardrails_and_evaluation_architecture.md | BySentencesChunker | 11    | 272.0   |         100.0% |
| performance_guardrails_and_evaluation_architecture.md | RecursiveChunker  | 17    | 176.9   |         100.0% |
| rag_system_design.md         | FixedSizeChunker (Baseline)  | 10    | 284.1   |           0.0% |
| rag_system_design.md         | BySentencesChunker | 5     | 476.0   |         100.0% |
| rag_system_design.md         | RecursiveChunker  | 18    | 132.8   |         100.0% |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker2 (`recursive2`) | 8/10 | 103 chunks, avg 142.60; khá ổn định, giữ ngữ cảnh tốt | Cài đặt custom khó chuẩn hóa hơn strategy gốc |
| Hieu | RecursiveChunker (`recursive`) | 8/10 | 102 chunks, avg 141.68; giữ cấu trúc tốt cho tài liệu dài | Tạo nhiều chunk hơn fixed-size nên top-k cần chọn hợp lý |
| Nam | FixedSizeChunker (`fixed_size`) | 6/10 | 92 chunks, avg 199.22; đơn giản, ổn định, dễ triển khai | Dễ cắt giữa ý, giảm chất lượng ngữ cảnh |
| Dung | SentenceChunker (`by_sentences`) | 7/10 | 30 chunks, avg 487.73; giữ nguyên câu, dễ đọc | Chunk dài, dễ vượt mức kỳ vọng trên tài liệu nhiều câu |
| Duc Anh | Custom LLM-guided chunking | 8/10 | 44 chunks, avg 375.09; chọn được policy phù hợp cho tài liệu spec | Phụ thuộc vào prompt/LLM, khó tái lập nếu không chuẩn hóa |
| Vinh | SentenceChunker (`by_sentences`) | 7/10 | 30 chunks, avg 487.73; giữ nguyên câu, dễ đọc | Chunk dài, dễ vượt mức kỳ vọng trên tài liệu nhiều câu |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *RecursiveChunker là strategy tốt nhất cho domain AI Architecture. Lý do là vì tài liệu kỹ thuật có cấu trúc Markdown phân tầng (Headers, Code blocks, Lists); RecursiveChunker giúp giữ tiêu đề và các khối mã nguồn đi liền với nhau, tránh việc các prompt hướng dẫn bị cắt rời, mã nguồn bị phân mảnh, từ đó giúp RAG Agent trả lời chính xác các câu hỏi kỹ thuật phức tạp.*

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Sử dụng Regex `[.!?]\s+` để xác định ranh giới giữa các câu. Sau khi tách văn bản thành danh sách các câu đơn lẻ, thì gộp chúng lại thành các nhóm dựa trên tham số `max_sentences_per_chunk` để đảm bảo mỗi chunk chứa một lượng thông tin vừa đủ mà không bị quá ngắn.*

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Thuật toán hoạt động theo cơ chế đệ quy: Nếu văn bản lớn hơn `chunk_size`, nó sẽ tìm ký tự phân cách có độ ưu tiên cao nhất (ví dụ `\n\n`) để chia đôi. Nếu không tìm thấy, nó chuyển xuống các cấp thấp hơn (`\n`, rồi ` `).*

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Dữ liệu được lưu trữ song song trong một dictionary (in-memory) phục vụ tìm kiếm nhanh và ChromaDB (persistence). Khi thực hiện `search`, tính toán Cosine Similarity giữa vector truy vấn và toàn bộ vector trong store, sau đó sắp xếp giảm dần theo điểm số để lấy ra Top-K kết quả liên quan nhất.*

**`search_with_filter` + `delete_document`** — approach:
> *Việc lọc được thực hiện trước khi tính toán độ tương đồng để giảm khối lượng tính toán. Với `delete_document`, mã nguồn sẽ xóa bản ghi dựa trên `doc_id` đồng thời ở cả in-memory storage và ChromaDB collection để đảm bảo tính nhất quán của dữ liệu.*

### KnowledgeBaseAgent

**`answer`** — approach:
> *Hệ thống thực hiện quy trình RAG chuẩn: Đầu tiên, câu hỏi của người dùng được chuyển đổi thành vector embedding. Sau đó, nó thực hiện tìm kiếm Top-K đoạn văn liên quan nhất từ Store. Cuối cùng, các đoạn văn này được nạp vào một cấu trúc System Prompt (context injection) cùng với câu hỏi để LLM có thể tổng hợp câu trả lời chính xác dựa trên dữ liệu thực tế thay vì dự đoán.*

### Bonus & Optimization

**What bonus features did you implement?**
> *Tôi đã triển khai **RecursiveChunker** với khả năng chia nhỏ văn bản đệ quy linh hoạt, giúp tăng Boundary Score lên 100%. Ngoài ra, tôi đã tích hợp thành công **ChromaDB** làm bộ lưu trữ Vector lâu dài, cho phép hệ thống duy trì cơ sở kiến thức ngay cả khi ứng dụng bị tắt.*

### Test Results

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.13s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | The system uses vector embeddings... | Vector embeddings are used by the system... | high | 0.8819 | Yes |
| 2 | Retrieval-augmented generation improves... | LLM responses are more accurate when... | high | 0.7779 | Yes |
| 3 | FastHTML is a Python web framework... | The CEO of Indeed mentioned a 20%... | low | 0.1482 | Yes |
| 4 | Pricing accuracy is essential... | User trust depends on accurate pricing... | high | 0.7188 | Yes |
| 5 | Performance guardrails ensure low latency... | The technical documentation is stored... | low | 0.1001 | Yes |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Kết quả từ mô hình `text-embedding-3-small` cho thấy khả năng nhận diện ngữ nghĩa cực kỳ mạnh mẽ khi xử lý các cấu trúc câu khác nhau (chủ động/bị động - Cặp 1 đạt 0.88). Một điểm đáng lưu ý là model nhạy cảm với các thuật ngữ viết tắt (acronyms); việc diễn giải rõ nghĩa (Cặp 2) giúp điểm số tăng vọt so với khi dùng từ viết tắt thô. Điều này khẳng định embeddings biểu diễn các "ý niệm" (concepts) trong không gian vector đa chiều một cách tinh tế, chứ không chỉ so khớp từ vựng.*

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

| # | Query | Top-1 Chunk (Preview) | Score | Relevant? |
|---|-------|----------------------|-------|-----------|
| 1 | What does Hermes do to handle cache billing correctly? | - handles cache billing correctly - distinguishes `actual` vs `estimated` vs `included` vs `unknown`... | 0.7245 | Yes |
| 2 | What are the four layers in the high-level pricing architecture? | 1. Normalize usage before pricing. 2. Never fold cached tokens into plain input cost. 3. Track certa... | 0.5708 | Yes |
| 3 | When should the UI show `included` instead of an estimated dollar amount? | Presentation rules:  - `actual`: show dollar amount as final - `estimated`: show dollar amount with ... | 0.6000 | No |
| 4 | In the ML guide, what are the three main machine learning paradigms? | @app.get("/models/{nm}") def model(nm:ModelName): return nm  print(cli.get('/models/alexnet').text) ... | 0.3184 | No |
| 5 | In the FastHTML tutorial, what is HTMX used for? | [HTMX](https://htmx.org/) addresses some key limitations of HTML. In vanilla HTML, links can trigger... | 0.6645 | Yes |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 1 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Cách quản lý dung lượng file Markdown lớn trong RAG bằng cách chia nhỏ theo các Header cấp 2 giúp truy xuất context cực kỳ chính xác.*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Tích hợp thành tiện ích trong project cá nhân.*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Tôi sẽ tập trung nhiều hơn vào việc làm sạch dữ liệu (data cleaning) đối với các file autogenerated như `fast_api.md` để loại bỏ các đoạn comment rác.*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 9 / 10 |
| Chunking strategy | Nhóm | 12 / 15 |
| My approach | Cá nhân | 9 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 9 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **87 / 100** |
