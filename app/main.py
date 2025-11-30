import os
from fastapi import FastAPI, UploadFile, File, Body, HTTPException
from google import genai
from app.utils import *
import chromadb
from chromadb.config import Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI()

chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(anonymized_telemetry=False)
)
collection = chroma_client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

@app.get("/")
async def root():
    return {"message": "The app is alive!!!!!!!!!!!!!!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")

        if not text.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        chunks = chunk_text(text, chunk_size=1000, overlap=200)

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for i, chunk in enumerate(chunks):
            emb = client.models.embed_content(
                model="models/text-embedding-004",
                contents=chunk
            ).embeddings[0].values

            ids.append(f"{file.filename}_chunk_{i}")
            embeddings.append(emb)
            metadatas.append({"filename": file.filename, "chunk": i})
            documents.append(chunk)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_llm(question: str = Body(..., embed=True)):
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        q_embedding = client.models.embed_content(
            model="models/text-embedding-004",
            contents=question
        ).embeddings[0].values

        results = collection.query(
            query_embeddings=[q_embedding],
            n_results=5
        )

        retrieved_docs = results.get("documents", [[]])[0]
        print(retrieved_docs)
        if not retrieved_docs:
            return {"response": "No relevant documents found."}

        context = "\n\n".join(retrieved_docs)

        final_prompt = generate_final_prompt(context, question)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt
        )

        return {
            "question": question,
            "answer": response.text,
            "sources": retrieved_docs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))