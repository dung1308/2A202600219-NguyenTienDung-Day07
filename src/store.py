from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401
            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(name=collection_name)
            # TODO: initialize chromadb client + collection
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # TODO: build a normalized stored record for one document
        # raise NotImplementedError("Implement EmbeddingStore._make_record")
        self._next_index += 1
        record = {
            "id": str(self._next_index),
            "doc_id": doc.id,
            "content": doc.content,
            "metadata": doc.metadata or {},
            "embedding": self._embedding_fn(doc.content)
        }
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # TODO: run in-memory similarity search over provided records
        # raise NotImplementedError("Implement EmbeddingStore._search_records")
        query_emb = self._embedding_fn(query)
        scored_records = []
        for record in records:
            score = _dot(query_emb, record["embedding"])
            scored_records.append((score, record))
            
        scored_records.sort(key=lambda x: x[0], reverse=True)
        ret = []
        for score, rec in scored_records[:top_k]:
            r = rec.copy()
            r["score"] = score
            ret.append(r)
        return ret

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        # TODO: embed each doc and add to store
        # raise NotImplementedError("Implement EmbeddingStore.add_documents")
        records = [self._make_record(doc) for doc in docs]
        if self._use_chroma and self._collection:
            ids = [r["id"] for r in records]
            documents = [r["content"] for r in records]
            embeddings = [r["embedding"] for r in records]
            metadatas = [r["metadata"] for r in records]
            self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        
        self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        # TODO: embed query, compute similarities, return top_k
        # raise NotImplementedError("Implement EmbeddingStore.search")
        if self._use_chroma and self._collection:
            query_emb = self._embedding_fn(query)
            results = self._collection.query(query_embeddings=[query_emb], n_results=top_k)
            ret = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    ret.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    })
            return ret
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        # TODO
        # raise NotImplementedError("Implement EmbeddingStore.get_collection_size")
        if self._use_chroma and self._collection:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # TODO: filter by metadata, then search among filtered chunks
        # raise NotImplementedError("Implement EmbeddingStore.search_with_filter")
        if not metadata_filter:
            return self.search(query, top_k)
            
        if self._use_chroma and self._collection:
            query_emb = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_emb], 
                n_results=top_k, 
                where=metadata_filter
            )
            ret = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    ret.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    })
            return ret
            
        filtered_records = []
        for record in self._store:
            match = True
            for k, v in metadata_filter.items():
                if record.get("metadata", {}).get(k) != v:
                    match = False
                    break
            if match:
                filtered_records.append(record)
                
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        # TODO: remove all stored chunks where metadata['doc_id'] == doc_id
        # raise NotImplementedError("Implement EmbeddingStore.delete_document")
        deleted = False
        if self._use_chroma and self._collection:
            initial_count = self._collection.count()
            self._collection.delete(where={"doc_id": doc_id})
            if self._collection.count() < initial_count:
                deleted = True
                
        initial_len = len(self._store)
        self._store = [r for r in self._store if r.get("doc_id") != doc_id]
        if len(self._store) < initial_len:
            deleted = True
            
        return deleted
