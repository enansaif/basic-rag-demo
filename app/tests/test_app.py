import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ask_llm():
    response = client.post("/ask")
    assert response.status_code == 200


def test_upload_file():
    test_file = io.BytesIO(b"sample content")

    response = client.post(
        "/upload",
        files={"file": ("test.txt", test_file, "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert data["filename"] == "test.txt"
