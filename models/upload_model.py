from dataclasses import dataclass
from typing import Optional
from enum import Enum


class UploadStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class FileInfo:
    filename: str
    relative_path: str
    size: int
    content_type: Optional[str] = None


@dataclass
class UploadRequest:
    files: list[FileInfo]
    destination_folder: str


@dataclass
class UploadResponse:
    status: UploadStatus
    message: str
    uploaded_files: list[str]
    failed_files: list[str]
    destination_path: str

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "message": self.message,
            "uploaded_files": self.uploaded_files,
            "failed_files": self.failed_files,
            "destination_path": self.destination_path,
        }
