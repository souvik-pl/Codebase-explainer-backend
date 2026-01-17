from langchain_core.tools import tool
from repositories.chroma_repository import chroma_repository


@tool
def search_codebase(query: str) -> str:
    """
    Search the codebase for relevant code chunks based on a natural language query.
    Use this to find functions, classes, imports, or any code related to the user's question.

    Args:
        query: A natural language description of what code to find.
               Examples: "authentication logic", "database connection", "API endpoints"

    Returns:
        Relevant code chunks with file paths and metadata.
    """
    results = chroma_repository.query(query, n_results=5)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return "No relevant code found in the codebase."

    formatted_results = []
    for doc, meta in zip(documents, metadatas):
        chunk_info = f"""
--- {meta.get('file_path', 'unknown')} ---
Type: {meta.get('chunk_type', 'unknown')} | Name: {meta.get('name', 'unknown')}
Lines: {meta.get('start_line', '?')}-{meta.get('end_line', '?')}
{'-' * 40}
{doc}
"""
        formatted_results.append(chunk_info)

    return "\n".join(formatted_results)


@tool
def search_by_file_type(file_extension: str, query: str) -> str:
    """
    Search for code in files with a specific extension.
    Use this when the user asks about a specific language or file type.

    Args:
        file_extension: The file extension to filter by (e.g., ".py", ".js", ".ts")
        query: What to search for within those files.

    Returns:
        Relevant code chunks from files matching the extension.
    """
    results = chroma_repository.query(query, n_results=10)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    filtered_results = []
    for doc, meta in zip(documents, metadatas):
        file_path = meta.get("file_path", "")
        if file_path.endswith(file_extension):
            chunk_info = f"""
--- {file_path} ---
Type: {meta.get('chunk_type', 'unknown')} | Name: {meta.get('name', 'unknown')}
Lines: {meta.get('start_line', '?')}-{meta.get('end_line', '?')}
{'-' * 40}
{doc}
"""
            filtered_results.append(chunk_info)

    if not filtered_results:
        return f"No relevant code found in {file_extension} files."

    return "\n".join(filtered_results)


@tool
def get_codebase_stats() -> str:
    """
    Get statistics about the indexed codebase.
    Use this to understand the scope of the codebase before answering questions.

    Returns:
        Statistics including total chunks and collection name.
    """
    stats = chroma_repository.get_stats()
    return f"Codebase contains {stats['total_documents']} indexed code chunks in collection '{stats['collection_name']}'."


@tool
def search_imports_and_dependencies(query: str) -> str:
    """
    Search specifically for imports, dependencies, and module-level code.
    Use this to understand what libraries and frameworks the codebase uses.

    Args:
        query: What dependency or import to look for (e.g., "flask", "database", "authentication")

    Returns:
        Import statements and module-level code related to the query.
    """
    results = chroma_repository.query(f"import {query}", n_results=10)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    filtered_results = []
    for doc, meta in zip(documents, metadatas):
        if meta.get("chunk_type") == "module" or "import" in doc.lower():
            chunk_info = f"""
--- {meta.get('file_path', 'unknown')} ---
{doc}
"""
            filtered_results.append(chunk_info)

    if not filtered_results:
        return f"No imports or dependencies found related to '{query}'."

    return "\n".join(filtered_results[:5])


all_tools = [
    search_codebase,
    search_by_file_type,
    get_codebase_stats,
    search_imports_and_dependencies,
]
