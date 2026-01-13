import chromadb
from chromadb import QueryResult
from chromadb.config import Settings

from models.chroma_model import ChromaStats


class ChromaRepository:
    COLLECTION_NAME = "codebase_explainer"
    PERSIST_DIR = "chroma_db"

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=self.PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.get_or_create_collection()

    def get_or_create_collection(self) -> chromadb.Collection:
        return self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "Codebase files for RAG"},
        )

    def clear_collection(self) -> None:
        self.client.delete_collection(name=self.COLLECTION_NAME)
        self.collection = self.get_or_create_collection()

    def get_stats(self) -> ChromaStats:
        return ChromaStats(
            total_documents=self.collection.count(),
            collection_name=self.COLLECTION_NAME,
        )

    def query(self, query_text: str, n_results: int = 5) -> QueryResult:
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )

    def add(self, ids: list[str], documents: list[str], metadatas: list[dict]) -> None:
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )


chroma_repository = ChromaRepository()
