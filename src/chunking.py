from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # TODO: split into sentences, group into chunks
        # raise NotImplementedError("Implement SentenceChunker.chunk")
        if not text:
            return []
        
        # Split on ". ", "! ", "? " or ".\n" using regex, keeping the separator if possible.
        # But a simple way is just using re.split with capture groups or simple replace.
        # Let's split using re.split capturing the punctuation to append it back.
        parts = re.split(r'([.!?]\s+|\.\n)', text)
        
        sentences = []
        current_sentence = ""
        for i in range(0, len(parts), 2):
            part = parts[i]
            sep = parts[i+1] if i+1 < len(parts) else ""
            full_sentence = (part + sep).strip()
            if full_sentence:
                sentences.append(full_sentence)
                
        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = " ".join(sentences[i : i + self.max_sentences_per_chunk])
            chunks.append(group)
            
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        # raise NotImplementedError("Implement RecursiveChunker.chunk")
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        # raise NotImplementedError("Implement RecursiveChunker._split")
        if len(current_text) <= self.chunk_size:
            return [current_text]
            
        if not remaining_separators:
            # We ran out of separators, need to force split by chunk_size
            chunks = []
            for i in range(0, len(current_text), self.chunk_size):
                chunks.append(current_text[i : i + self.chunk_size])
            return chunks
            
        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]
        
        if separator == "":
            parts = list(current_text)
        else:
            parts = current_text.split(separator)
            
        final_chunks = []
        current_chunk = ""
        
        for i, part in enumerate(parts):
            # Append separator only if it's not the last part and not splitting by characters
            append_str = separator if i < len(parts) - 1 and separator != "" else ""
            segment = part + append_str
            
            if len(current_chunk) + len(segment) <= self.chunk_size:
                current_chunk += segment
            else:
                if current_chunk:
                    final_chunks.append(current_chunk)
                current_chunk = segment
                if len(current_chunk) > self.chunk_size:
                    # Recursive call if still over limit
                    final_chunks.extend(self._split(current_chunk, next_separators))
                    current_chunk = ""
                    
        if current_chunk:
            if len(current_chunk) > self.chunk_size:
                final_chunks.extend(self._split(current_chunk, next_separators))
            else:
                final_chunks.append(current_chunk)
                
        return final_chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    # raise NotImplementedError("Implement compute_similarity")
    dot_product = _dot(vec_a, vec_b)
    mag_a = math.sqrt(_dot(vec_a, vec_a))
    mag_b = math.sqrt(_dot(vec_b, vec_b))
    
    if mag_a == 0 or mag_b == 0:
        return 0.0
        
    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        # raise NotImplementedError("Implement ChunkingStrategyComparator.compare")
        fixed = FixedSizeChunker(chunk_size=chunk_size)
        sentence = SentenceChunker()
        recurse = RecursiveChunker(chunk_size=chunk_size)
        
        fixed_chunks = fixed.chunk(text)
        sentence_chunks = sentence.chunk(text)
        recurse_chunks = recurse.chunk(text)
        
        return {
            "fixed_size": {
                "count": len(fixed_chunks),
                "avg_length": sum(len(c) for c in fixed_chunks) / len(fixed_chunks) if fixed_chunks else 0,
                "chunks": fixed_chunks
            },
            "by_sentences": {
                "count": len(sentence_chunks),
                "avg_length": sum(len(c) for c in sentence_chunks) / len(sentence_chunks) if sentence_chunks else 0,
                "chunks": sentence_chunks
            },
            "recursive": {
                "count": len(recurse_chunks),
                "avg_length": sum(len(c) for c in recurse_chunks) / len(recurse_chunks) if recurse_chunks else 0,
                "chunks": recurse_chunks
            }
        }
