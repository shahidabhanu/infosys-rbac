# rag.py
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Load FAISS index and metadata
index = faiss.read_index("vector_store.index")
with open("metadata.pkl", "rb") as f:
    metadata_list = pickle.load(f)

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Role-based access control
ROLE_ACCESS = {
    "employee": ["general"],
    "finance": ["finance", "general"],
    "hr": ["hr", "general", "contacts"],
    "c_level": ["finance", "hr", "engineering", "marketing", "general", "contacts"],
    "admin": ["finance", "hr", "engineering", "marketing", "general", "contacts"]
}

def check_access(user_role, doc_role):
    return doc_role in ROLE_ACCESS.get(user_role, [])

def query_rag(user_role, query, top_k=3):
    # Encode query
    q_emb = model.encode([query])[0].astype('float32')
    
    # Search
    D, I = index.search(np.array([q_emb]), top_k)
    
    # Filter by role
    results = []
    for idx in I[0]:
        doc = metadata_list[idx]
        if check_access(user_role, doc["role"]):
            results.append(doc["text"])
    return results if results else ["Access Denied"]

# Example usage
if __name__ == "__main__":
    user_role = "hr"  # change for testing
    query = "Show me all employees contact details"
    answer = query_rag(user_role, query)
    print("Answer:", answer)
