## Setup and Run Instructions

### Prerequisites
- Docker and Docker Compose
- Google Gemini API key

### Environment Variables
Create a `.env` file in the project root and set Gemini API key like .env.template

### Running with Docker Compose
```bash
docker-compose up --build
```

The application will be available at:
- API: http://localhost:8000

## Architecture Overview
Basic RAG pipeline.
- /upload: Documnets -> document processor -> document chunks -> embeddings -> ChromaDB
- /ask: Question -> retriever(retrieve vector from ChromaDB) -> vector + prompt -> LLM -> Final Generation

## File/Module Responsibilities

### `app/main.py`
- Defines API endpoints: `/upload` (POST) and `/ask` (POST)
- Handles file uploads (up to 3 files) and question processing

### `app/config.py`
- Configuration management class
- Manages environment variables and model settings

### `app/utils.py`
- `chunk_text()`: Splits documents into overlapping chunks
- `extract_text_from_pdf()`: Extracts text from PDF
- `process_chunks()`: Generates embeddings for document chunks
- `query_db()`: Performs semantic search in ChromaDB
- `generate_final_prompt()`: Constructs RAG prompt with context and question

### `app/tests/test_app.py`
- Unit tests for API endpoints
- Tests file upload and question-answering functionality

## Design Decisions & Trade-offs

FastAPI Framework: Chosen for its async capabilities, automatic OpenAPI documentation.
ChromaDB for Vector Storage: Selected for its simplicity, and my pre existing experience with it.
Google Gemini API: Utilized for both embeddings and text generation to maintain consistency and reduce API complexity.
Simple Chunking and Retrieval Strategy: I would have used langchain for bigger projects but for simple RAG pipeline i kept everything simple.

## Limitations

Supported Formats: only pdf and plain text files are supported.
Concurrent Uploads: no batch processing for larger document sets.
Basic Error Handling: needed more time.
Fixed Chunking: there are faar more complex chunking techniques out there.
No Caching: repeated query will not be cached.
Basic Generation Prompt: again would use langchain for complex projects, with their rich prompt library.

## Future Improvements

Points in the limitations section would be considered for future improvements.
