# === File: backend/schemas.py ===
from pydantic import BaseModel, EmailStr
from typing import List

class PredictRequest(BaseModel):
    address: str

class PredictResponse(BaseModel):
    prediction: int
    probability_illicit: float

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

