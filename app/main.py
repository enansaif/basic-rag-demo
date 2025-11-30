from app.config import config
from fastapi import FastAPI, UploadFile, File, Body, HTTPException
from fastapi.responses import RedirectResponse
from app import utils

app = FastAPI()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")

        if not text.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        chunks = utils.chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

        ids, embeddings, metadatas, documents = utils.process_chunks(chunks, config, file.filename)

        config.collection.upsert(
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

        results = utils.query_db(question, config)

        retrieved_docs = results.get("documents", [[]])[0]
        if not retrieved_docs:
            return {"response": "No relevant documents found."}

        context = "\n\n".join(retrieved_docs)

        final_prompt = utils.generate_final_prompt(context, question)

        response = config.llm_client.models.generate_content(
            model=config.GENERATION_MODEL,
            contents=final_prompt
        )

        return {
            "question": question,
            "answer": response.text,
            "sources": retrieved_docs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
