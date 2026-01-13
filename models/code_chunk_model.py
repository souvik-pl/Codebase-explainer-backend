from dataclasses import dataclass
from typing import Optional


@dataclass
class CodeChunk:
    content: str
    chunk_type: str
    name: str
    file_path: str
    language: str
    start_line: int
    end_line: int
    parent_class: Optional[str] = None

    def to_document(self) -> str:
        header = f"File: {self.file_path}"
        if self.parent_class:
            header += f"\nClass: {self.parent_class}"
        header += f"\nType: {self.chunk_type}"
        header += f"\nName: {self.name}"
        return f"{header}\n\n{self.content}"

    def to_metadata(self) -> dict:
        return {
            "file_path": self.file_path,
            "chunk_type": self.chunk_type,
            "name": self.name,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "parent_class": self.parent_class or "",
        }
