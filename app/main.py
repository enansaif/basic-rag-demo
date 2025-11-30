from app.config import config
from fastapi import FastAPI, UploadFile, File, Body, HTTPException
from fastapi.responses import RedirectResponse
from app import utils

app = FastAPI()

async def process_single_file(file):
    content = await file.read()

    if file.content_type == "application/pdf":
        text = utils.extract_text_from_pdf(content)
    else:
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

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    if len(files) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 files allowed.")

    results = []
    for file in files:
        result = await process_single_file(file)
        results.append(result)

    return {
        "status": "success",
        "files": results
    }


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
