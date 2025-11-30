from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "The app is alive!!!!!!!!!!!!!!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

@app.post("/ask")
async def ask_llm():
    return {"response": "Hello World"}