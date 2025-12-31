# config.py
# Central configuration file for the project

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data", "documents")

# Vector store directory
VECTOR_DB_DIR = os.path.join(BASE_DIR, "..", "..", "data", "vector_db")

# Embedding model name
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# JWT settings (for future use / explanation)
SECRET_KEY = "infosys-internal-chatbot-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Allowed roles in the system
ALLOWED_ROLES = [
    "employee",
    "finance",
    "hr",
    "engineering",
    "marketing",
    "c-level",
    "admin"
]
