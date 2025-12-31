from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.users import USERS

SECRET_KEY = "secret123"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])

def authenticate_user(username, password):
    user = USERS.get(username)
    if not user or user["password"] != password:
        return None
    return {"username": username, "role": user["role"]}

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
