from dataclasses import dataclass


@dataclass
class ChromaStats:
    total_documents: int
    collection_name: str
