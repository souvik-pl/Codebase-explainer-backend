# Codebase Explainer

An intelligent codebase analysis and explanation tool that uses AI to help you understand and explore code repositories. Built with Flask, LangGraph, and ChromaDB for efficient code retrieval and natural language querying.

**Frontend Repository**: [Codebase Explainer Frontend](https://github.com/souvik-pl/Codebase-explainer-frontend)

## Features

- **🔍 Smart Code Search**: Upload and index entire codebases for intelligent searching
- **🤖 AI-Powered Explanations**: Get detailed explanations of code using advanced language models
- **📊 Multi-Language Support**: Supports Python, JavaScript, TypeScript, Java, Go, Rust, C, and C++
- **🌐 REST API**: Clean RESTful API for integration with other tools
- **💾 Vector Storage**: Uses ChromaDB for efficient semantic code retrieval
- **🎯 RAG Architecture**: Retrieval-Augmented Generation for accurate, context-aware responses

## Architecture

The application follows a clean, modular architecture:

```
├── api/                    # Flask API endpoints
│   ├── query_api.py       # Query handling endpoint
│   └── upload_api.py      # File upload endpoint
├── langgraph_agent/        # AI agent implementation
│   ├── agents.py          # Agent logic and tools
│   ├── graph.py           # LangGraph workflow
│   ├── prompts.py         # System prompts
│   └── tools.py           # Search and analysis tools
├── models/                 # Pydantic data models
├── repositories/           # Data access layer
├── services/              # Business logic layer
└── utils/                 # Utility functions
```

## Tech Stack

- **Backend**: Flask 3.0+ with Flask-CORS
- **AI/ML**: 
  - LangChain & LangGraph for agent orchestration
  - Groq for LLM inference (GPT-OSS-120B model)
- **Database**: ChromaDB for vector storage and similarity search
- **Parsing**: Tree-sitter for multi-language code parsing
- **Development**: Black for code formatting

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Codebase-explainer
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

### Running the Application

Start the Flask development server:
```bash
python main.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### Upload Codebase
```bash
POST /api/upload/folder
Content-Type: multipart/form-data

# Upload multiple files with folder name
curl -X POST http://localhost:5000/api/upload/folder \
  -F "files=@file1.py" \
  -F "files=@file2.js" \
  -F "folder_name=my_project"
```

#### Query Codebase
```bash
GET /api/query?q=your_question_here

# Example:
curl "http://localhost:5000/api/query?q=How is authentication implemented?"
```

### Standalone Query Tool

Use the standalone script to query the database directly:
```bash
python query_db.py
```

This interactive tool allows you to:
- Check database statistics
- Query the indexed codebase
- View similarity scores and file locations

## How It Works

1. **Indexing**: When you upload files, they are parsed using tree-sitter and split into semantic chunks
2. **Embedding**: Code chunks are converted to vector embeddings and stored in ChromaDB
3. **Querying**: When you ask a question, the system:
   - Retrieves relevant code chunks using similarity search
   - Passes the context to an AI agent with specialized tools
   - Generates a comprehensive explanation in HTML format

## Supported Languages

- Python
- JavaScript
- TypeScript
- Java
- Go
- Rust
- C/C++

## Development

### Code Formatting

The project uses Black for code formatting:
```bash
uv run black .
```

### Project Structure

- **API Layer**: Handles HTTP requests and responses
- **Service Layer**: Contains business logic
- **Agent Layer**: Implements AI reasoning and tool usage
- **Repository Layer**: Manages data persistence
- **Models**: Defines data structures using Pydantic


## Requirements

- Python 3.11+
- Groq API key
