import os
from google import genai
import chromadb
from chromadb.config import Settings


class Config:
    def __init__(self):
        # env
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.CHROMA_HOST = os.getenv("CHROMA_HOST")
        self.CHROMA_PORT = os.getenv("CHROMA_PORT")

        # models
        self.EMBEDDING_MODEL = "models/text-embedding-004"
        self.GENERATION_MODEL = "gemini-2.5-flash"

        # doc process
        self.CHUNK_SIZE = 1000
        self.CHUNK_OVERLAP = 200

        # clients
        self.llm_client = genai.Client(api_key=self.GEMINI_API_KEY)

        self.vdb_client = chromadb.HttpClient(
            host=self.CHROMA_HOST,
            port=self.CHROMA_PORT,
            settings=Settings(anonymized_telemetry=False)
        )

        # db
        self.collection = self.vdb_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )


config = Config()
