def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start, end = 0, chunk_size

    while start < len(text):
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
        end = start + chunk_size

    return chunks


def generate_final_prompt(context, question):
    prompt = f"""
        Use the following context to answer.

        CONTEXT:
        {context}

        QUESTION:
        {question}

        If the context does not contain the answer, say "I don’t know."
    """
    return prompt


def query_db(question, config):
    q_embedding = config.llm_client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=question
    ).embeddings[0].values

    results = config.collection.query(
        query_embeddings=[q_embedding],
        n_results=5
    )
    return results


def process_chunks(chunks, config, filename):
    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for i, chunk in enumerate(chunks):
        emb = config.llm_client.models.embed_content(
            model="models/text-embedding-004",
            contents=chunk
        ).embeddings[0].values

        ids.append(f"{filename}_chunk_{i}")
        embeddings.append(emb)
        metadatas.append({"filename": filename, "chunk": i})
        documents.append(chunk)
    return ids, embeddings, metadatas, documents
