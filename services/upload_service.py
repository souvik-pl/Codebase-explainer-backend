from werkzeug.datastructures import FileStorage

from models.upload_model import UploadResponse, UploadStatus
from repositories.chroma_repository import chroma_repository
from services.code_chunk_service import code_chunk_service

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".swift",
    ".kt",
    ".scala",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".vue",
    ".svelte",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".md",
    ".txt",
    ".sh",
    ".sql",
    ".graphql",
    ".proto",
    ".dockerfile",
    ".env",
    ".gitignore",
}


class UploadService:
    def sanitize_path(self, path: str) -> str:
        return path.replace("..", "").lstrip("/").lstrip("\\")

    def is_supported_file(self, filename: str) -> bool:
        if not filename:
            return False
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        base_name = filename.rsplit("/", 1)[-1] if "/" in filename else filename
        return ext in SUPPORTED_EXTENSIONS or base_name in {
            ".gitignore",
            ".env",
            "Dockerfile",
            "Makefile",
        }

    def read_file_content(self, file: FileStorage) -> str | None:
        try:
            content = file.read()
            file.seek(0)
            return content.decode("utf-8", errors="ignore")
        except Exception:
            return None

    def upload_folder(
        self, files: list[FileStorage], folder_name: str
    ) -> UploadResponse:
        uploaded_files: list[str] = []
        failed_files: list[str] = []
        skipped_files: list[str] = []

        chroma_repository.clear_collection()

        for file in files:
            if not file.filename:
                continue

            relative_path = self.sanitize_path(file.filename)

            if not self.is_supported_file(relative_path):
                skipped_files.append(relative_path)
                continue

            try:
                content = self.read_file_content(file)
                if content is None or not content.strip():
                    skipped_files.append(f"{relative_path} (empty or unreadable)")
                    continue

                file_id = f"{relative_path}".replace("/", "_").replace("\\", "_")

                self.chunk_file(
                    file_id=file_id,
                    content=content,
                    file_path=relative_path,
                )
                uploaded_files.append(relative_path)

            except Exception as e:
                failed_files.append(f"{relative_path}: {str(e)}")

        if not uploaded_files and failed_files:
            status = UploadStatus.FAILED
            message = "All files failed to process"
        elif failed_files:
            status = UploadStatus.PARTIAL
            message = f"Indexed {len(uploaded_files)} files, {len(failed_files)} failed, {len(skipped_files)} skipped"
        else:
            status = UploadStatus.SUCCESS
            message = f"Successfully indexed {len(uploaded_files)} files into ChromaDB"

        stats = chroma_repository.get_stats()

        return UploadResponse(
            status=status,
            message=message,
            uploaded_files=uploaded_files,
            failed_files=failed_files,
            destination_path=f"ChromaDB collection: {stats.collection_name} ({stats.total_documents} chunks)",
        )

    def chunk_file(
        self,
        file_id: str,
        content: str,
        file_path: str,
    ) -> int:
        chunks = code_chunk_service.chunk_code(content, file_path)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_id}_{chunk.chunk_type}_{chunk.name}_{i}"
            chunk_id = chunk_id.replace(" ", "_").replace("/", "_")

            chroma_repository.add(
                ids=[chunk_id],
                documents=[chunk.to_document()],
                metadatas=[chunk.to_metadata()],
            )

        return len(chunks)


upload_service = UploadService()
