# models.py
# Pydantic models for request and response validation

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    role: Optional[str] = None
    message: str


class ChatRequest(BaseModel):
    query: str
    role: str


class ChatResponse(BaseModel):
    answer: str
    source: Optional[str] = None
