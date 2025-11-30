def chunk_text(text, chunk_size = 1000, overlap = 200):
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