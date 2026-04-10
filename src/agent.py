from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        # TODO: store references to store and llm_fn
        # pass
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # TODO: retrieve chunks, build prompt, call llm_fn
        # raise NotImplementedError("Implement KnowledgeBaseAgent.answer")
        results = self.store.search(question, top_k)
        if not results:
            context = "No relevant context found."
        else:
            context = "\n\n---\n\n".join([r['content'] for r in results])
            
        prompt = (
            f"Please answer the question based ONLY on the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        return self.llm_fn(prompt)
