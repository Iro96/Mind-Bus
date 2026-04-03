from typing import List, Dict, Any
import re

class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces with overlap."""
        if metadata is None:
            metadata = {}

        # Simple sentence-based chunking
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = len(sentence.split())  # Rough token count

            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "token_count": current_tokens,
                    "metadata": metadata.copy()
                })
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.overlap)
                current_chunk = overlap_text + " " + sentence
                current_tokens = len((overlap_text + " " + sentence).split())
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens

        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "token_count": current_tokens,
                "metadata": metadata.copy()
            })

        return chunks

    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """Get overlap text from the end of the chunk."""
        words = text.split()
        if len(words) <= overlap_tokens:
            return text
        return " ".join(words[-overlap_tokens:])

# Global instance
chunker = TextChunker()