# AI Model Performance Guardrails & Evaluation Architecture

Date: 2026-04-10

## Goal

Hệ thống nhằm đảm bảo mọi phản hồi từ AI không chỉ đạt chuẩn về mặt kỹ thuật mà còn phải duy trì tính ổn định về độ trễ (latency), độ chính xác (accuracy) và sự phù hợp về ngữ cảnh (context relevance). 

Thiết kế này thay thế các bộ kiểm tra thủ công hiện tại trong:
- `agent/output_parser.py`
- `evals/simple_bench.py`
- `gateway/routing_logic.py`

Bằng một hệ thống giám sát thời gian thực có khả năng:
- Tự động phát hiện suy giảm chất lượng (Model Drift).
- Phân loại lỗi theo mức độ nghiêm trọng (Hallucination vs. Formatting).
- Điều hướng yêu cầu (Routing) dựa trên hiệu năng thực tế thay vì chỉ số tĩnh.
- Cung cấp cơ chế "Circuit Breaker" khi mô hình có dấu hiệu phản hồi rác (gibberish).

## Problems In The Current Design

1. **Heuristic-based Validation**: Sử dụng Regex đơn giản để kiểm tra định dạng, không phát hiện được lỗi logic hoặc sự sai lệch về dữ liệu (hallucinations).
2. **Static Model Routing**: Hệ thống chọn mô hình dựa trên độ ưu tiên cứng, không quan tâm đến việc mô hình đó đang bị nghẽn (throttling) hoặc đang có tỉ lệ lỗi cao tại thời điểm đó.
3. **Lack of Semantic Evaluation**: Chỉ đo lường được "nó có phản hồi hay không", chứ không đo lường được "phản hồi đó có đúng với yêu cầu người dùng hay không".
4. **No Feedback Loop**: Dữ liệu từ các phản hồi lỗi không được quay vòng để cải thiện bộ prompt hoặc điều chỉnh tham số mô hình.

## Design Principles

1. **Evaluation-as-a-Service**: Tách biệt logic đánh giá khỏi logic nghiệp vụ của Agent.
2. **Semantic Similarity over Strict Matching**: Sử dụng Vector Embeddings để so sánh kết quả thay vì so sánh chuỗi ký tự.
3. **Graceful Degradation**: Nếu mô hình chính gặp sự cố về chất lượng, hệ thống tự động hạ cấp xuống mô hình ổn định hơn (fallback).
4. **Observability First**: Mọi phản hồi đều đi kèm với "Quality Score" trước khi đến tay người dùng.

## High-Level Architecture

Hệ thống bao gồm 4 lớp chính:



1. **Input Sanitization & Context Injection**: Chuẩn hóa Prompt và làm giàu dữ liệu đầu vào.
2. **Real-time Evaluator (The Guardrail)**: Chạy song song hoặc ngay sau khi mô hình sinh kết quả để chấm điểm.
3. **Dynamic Router**: Quyết định chấp nhận kết quả, yêu cầu sinh lại (retry), hoặc chuyển sang mô hình khác.
4. **Post-hoc Analytics & Fine-tuning**: Tổng hợp dữ liệu để tinh chỉnh (fine-tune) hoặc cập nhật RAG.

---

## Canonical Performance Record

Mọi yêu cầu AI phải sinh ra một bản ghi hiệu năng chuẩn hóa:

```python
@dataclass
class PerformanceRecord:
    request_id: str
    model_identity: str  # e.g., "openai:gpt-4o-2024-08-06"
    
    # Latency Metrics
    time_to_first_token_ms: int
    total_duration_ms: int
    tokens_per_second: float

    # Quality Metrics
    faithfulness_score: float  # Khả năng dựa trên dữ liệu đầu vào
    relevance_score: float     # Độ liên quan đến câu hỏi
    hallucination_detected: bool
    
    # Routing Info
    is_fallback: bool = False
    retry_count: int = 0