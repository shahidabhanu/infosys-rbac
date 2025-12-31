# ingest_docs.py
import os
import pickle
from sentence_transformers import SentenceTransformer
import faiss


from config import DATA_DIR, VECTOR_DB_DIR, EMBEDDING_MODEL


def load_documents():
    documents = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            role = filename.replace(".txt", "").lower()
            file_path = os.path.join(DATA_DIR, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            documents.append({
                "text": text,
                "role": role,
                "source": filename
            })

    return documents


def create_vector_store():
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    documents = load_documents()

    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [doc["text"] for doc in documents]
    embeddings = model.encode(texts)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(index, os.path.join(VECTOR_DB_DIR, "index.faiss"))

    # Save metadata
    with open(os.path.join(VECTOR_DB_DIR, "metadata.pkl"), "wb") as f:
        pickle.dump(documents, f)

    print("✅ Vector store created successfully")


if __name__ == "__main__":
    create_vector_store()
