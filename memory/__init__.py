from .schemas import (
    BaseMemory,
    EpisodicMemory,
    SemanticMemory,
    CorrectionMemory,
    MemoryExtractionRequest,
    MemoryExtractionResponse,
)
from .scoring import MemoryScorer

__all__ = [
    "BaseMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "CorrectionMemory",
    "MemoryExtractionRequest",
    "MemoryExtractionResponse",
    "MemoryScorer",
    "MemoryExtractor",
    "LongTermMemoryManager",
    "CorrectionMemoryHandler",
    "ShortTermMemory"
]


def __getattr__(name):
    if name == "MemoryExtractor":
        from .extraction import MemoryExtractor
        return MemoryExtractor
    if name == "LongTermMemoryManager":
        from .long_term import LongTermMemoryManager
        return LongTermMemoryManager
    if name == "CorrectionMemoryHandler":
        from .correction import CorrectionMemoryHandler
        return CorrectionMemoryHandler
    if name == "ShortTermMemory":
        from .short_term import ShortTermMemory
        return ShortTermMemory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
