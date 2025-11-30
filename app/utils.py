def chunk_text(text, chunk_size = 1000, overlap = 200):
    chunks = []
    start, end = 0, chunk_size

    while start < len(text):
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
        end = start + chunk_size

    return chunks
