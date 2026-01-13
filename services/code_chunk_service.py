from typing import Optional

import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_java as tsjava
import tree_sitter_go as tsgo
import tree_sitter_rust as tsrust
import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser

from models.code_chunk_model import CodeChunk

LANGUAGE_CONFIG = {
    "python": {
        "language": Language(tspython.language()),
        "function_query": "(function_definition name: (identifier) @name) @function",
        "class_query": "(class_definition name: (identifier) @name) @class",
        "method_query": "(class_definition body: (block (function_definition name: (identifier) @name) @method))",
    },
    "javascript": {
        "language": Language(tsjavascript.language()),
        "function_query": """[
            (function_declaration name: (identifier) @name) @function
            (arrow_function) @function
            (method_definition name: (property_identifier) @name) @method
        ]""",
        "class_query": "(class_declaration name: (identifier) @name) @class",
    },
    "typescript": {
        "language": Language(tstypescript.language_typescript()),
        "function_query": """[
            (function_declaration name: (identifier) @name) @function
            (arrow_function) @function
            (method_definition name: (property_identifier) @name) @method
        ]""",
        "class_query": "(class_declaration name: (identifier) @name) @class",
    },
    "tsx": {
        "language": Language(tstypescript.language_tsx()),
        "function_query": """[
            (function_declaration name: (identifier) @name) @function
            (arrow_function) @function
            (method_definition name: (property_identifier) @name) @method
        ]""",
        "class_query": "(class_declaration name: (identifier) @name) @class",
    },
    "java": {
        "language": Language(tsjava.language()),
        "function_query": "(method_declaration name: (identifier) @name) @function",
        "class_query": "(class_declaration name: (identifier) @name) @class",
    },
    "go": {
        "language": Language(tsgo.language()),
        "function_query": "(function_declaration name: (identifier) @name) @function",
        "class_query": "(type_declaration (type_spec name: (type_identifier) @name)) @class",
    },
    "rust": {
        "language": Language(tsrust.language()),
        "function_query": "(function_item name: (identifier) @name) @function",
        "class_query": """[
            (struct_item name: (type_identifier) @name) @class
            (impl_item) @class
        ]""",
    },
    "c": {
        "language": Language(tsc.language()),
        "function_query": "(function_definition declarator: (function_declarator declarator: (identifier) @name)) @function",
        "class_query": "(struct_specifier name: (type_identifier) @name) @class",
    },
    "cpp": {
        "language": Language(tscpp.language()),
        "function_query": "(function_definition declarator: (function_declarator declarator: (identifier) @name)) @function",
        "class_query": "(class_specifier name: (type_identifier) @name) @class",
    },
}

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
}


class CodeChunkService:
    def __init__(self):
        self.parsers: dict[str, Parser] = {}
        self.init_parsers()

    def init_parsers(self) -> None:
        for lang_name, config in LANGUAGE_CONFIG.items():
            parser = Parser(config["language"])
            self.parsers[lang_name] = parser

    def get_language_from_extension(self, file_path: str) -> Optional[str]:
        ext = "." + file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
        return EXTENSION_TO_LANGUAGE.get(ext)

    def supports_language(self, file_path: str) -> bool:
        return self.get_language_from_extension(file_path) is not None

    def chunk_code(self, content: str, file_path: str) -> list[CodeChunk]:
        language = self.get_language_from_extension(file_path)

        if not language or language not in LANGUAGE_CONFIG:
            return self.fallback_chunk(content, file_path)

        try:
            return self.semantic_chunk(content, file_path, language)
        except Exception:
            return self.fallback_chunk(content, file_path)

    def semantic_chunk(
        self, content: str, file_path: str, language: str
    ) -> list[CodeChunk]:
        chunks: list[CodeChunk] = []
        config = LANGUAGE_CONFIG[language]
        parser = self.parsers[language]

        tree = parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node
        lines = content.split("\n")

        processed_ranges: set[tuple[int, int]] = set()

        if "class_query" in config:
            class_query = config["language"].query(config["class_query"])
            class_captures = class_query.captures(root_node)

            for node, capture_name in class_captures:
                if capture_name == "class":
                    range_key = (node.start_point[0], node.end_point[0])
                    if range_key in processed_ranges:
                        continue
                    processed_ranges.add(range_key)

                    class_name = self.get_node_name(node, class_captures, language)
                    class_content = self.get_node_text(node, lines)

                    chunks.append(
                        CodeChunk(
                            content=class_content,
                            chunk_type="class",
                            name=class_name,
                            file_path=file_path,
                            language=language,
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                        )
                    )

        if "function_query" in config:
            func_query = config["language"].query(config["function_query"])
            func_captures = func_query.captures(root_node)

            for node, capture_name in func_captures:
                if capture_name in ("function", "method"):
                    range_key = (node.start_point[0], node.end_point[0])
                    if range_key in processed_ranges:
                        continue

                    if self.is_inside_class(node, processed_ranges):
                        continue

                    processed_ranges.add(range_key)

                    func_name = self.get_node_name(node, func_captures, language)
                    func_content = self.get_node_text(node, lines)
                    parent_class = self.find_parent_class(node, language)

                    chunks.append(
                        CodeChunk(
                            content=func_content,
                            chunk_type="method" if parent_class else "function",
                            name=func_name,
                            file_path=file_path,
                            language=language,
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                            parent_class=parent_class,
                        )
                    )

        if not chunks:
            return self.fallback_chunk(content, file_path, language)

        return chunks

    def fallback_chunk(
        self,
        content: str,
        file_path: str,
        language: str = "unknown",
        chunk_size: int = 1500,
        overlap: int = 200,
    ) -> list[CodeChunk]:
        if not content.strip():
            return []

        chunks: list[CodeChunk] = []
        lines = content.split("\n")
        current_chunk: list[str] = []
        current_size = 0
        chunk_start_line = 1

        for i, line in enumerate(lines):
            line_size = len(line) + 1

            if current_size + line_size > chunk_size and current_chunk:
                chunk_content = "\n".join(current_chunk)
                chunks.append(
                    CodeChunk(
                        content=chunk_content,
                        chunk_type="module",
                        name=f"chunk_{len(chunks) + 1}",
                        file_path=file_path,
                        language=language,
                        start_line=chunk_start_line,
                        end_line=chunk_start_line + len(current_chunk) - 1,
                    )
                )

                overlap_lines = []
                overlap_size = 0
                for prev_line in reversed(current_chunk):
                    if overlap_size + len(prev_line) + 1 > overlap:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_size += len(prev_line) + 1

                current_chunk = overlap_lines
                current_size = overlap_size
                chunk_start_line = i + 1 - len(overlap_lines)

            current_chunk.append(line)
            current_size += line_size

        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            chunks.append(
                CodeChunk(
                    content=chunk_content,
                    chunk_type="module",
                    name=f"chunk_{len(chunks) + 1}",
                    file_path=file_path,
                    language=language,
                    start_line=chunk_start_line,
                    end_line=chunk_start_line + len(current_chunk) - 1,
                )
            )

        return chunks

    def get_node_name(self, node, captures: list, language: str) -> str:
        for captured_node, capture_name in captures:
            if capture_name == "name":
                if (
                    captured_node.start_point[0] >= node.start_point[0]
                    and captured_node.end_point[0] <= node.end_point[0]
                ):
                    return captured_node.text.decode("utf-8")

        if node.type == "arrow_function":
            parent = node.parent
            if parent and parent.type == "variable_declarator":
                name_node = parent.child_by_field_name("name")
                if name_node:
                    return name_node.text.decode("utf-8")

        return "anonymous"

    def get_node_text(self, node, lines: list[str]) -> str:
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        return "\n".join(lines[start_line : end_line + 1])

    def is_inside_class(self, node, processed_ranges: set[tuple[int, int]]) -> bool:
        node_start = node.start_point[0]
        node_end = node.end_point[0]

        for class_start, class_end in processed_ranges:
            if class_start < node_start and node_end < class_end:
                return True
        return False

    def find_parent_class(self, node, language: str) -> Optional[str]:
        current = node.parent
        class_types = {
            "python": "class_definition",
            "javascript": "class_declaration",
            "typescript": "class_declaration",
            "tsx": "class_declaration",
            "java": "class_declaration",
            "cpp": "class_specifier",
        }

        class_type = class_types.get(language)
        if not class_type:
            return None

        while current:
            if current.type == class_type:
                name_node = current.child_by_field_name("name")
                if name_node:
                    return name_node.text.decode("utf-8")
            current = current.parent
        return None


code_chunk_service = CodeChunkService()
