# === File: backend/main.py ===
import schemas
from fastapi import FastAPI, HTTPException, Depends
from schemas import PredictRequest, PredictResponse
from models import UserFeatures, AuthUser
from db import SessionLocal, engine, Base
from fetch_features import get_features_from_etherscan
import joblib
import numpy as np
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)
app = FastAPI()

model_path = "xgboost_model.pkl"
scaler_path = "scaler.pkl"
encoder_path = "token_type_encoder.pkl"

print("Checking for model:", os.path.exists(model_path))
print("Checking for scaler:", os.path.exists(scaler_path))
print("Checking for encoder:", os.path.exists(encoder_path))

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
token_encoder = joblib.load(encoder_path)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def signup_user(req: schemas.SignupRequest, db: Session = Depends(get_db)):
    try:
        if db.query(AuthUser).filter((AuthUser.username == req.username) | (AuthUser.email == req.email)).first():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        hashed_password = pwd_context.hash(req.password)
        new_user = AuthUser(username=req.username, email=req.email, password=hashed_password)
        db.add(new_user)
        db.commit()
        return {"message": "Signup successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login_user(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AuthUser).filter_by(username=req.username).first()
    if not user or not pwd_context.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user": user.username}

@app.post("/predict", response_model=PredictResponse)
def predict_account(req: PredictRequest):
    try:
        print(f"🔍 Received address: {req.address}")

        # Extract features from the address
        features = get_features_from_etherscan(req.address, token_encoder)
        print(f"✅ Feature vector length: {len(features)}")
        print(f"📦 Features (first 5): {features[:5]}")

        # Check if length is exactly 50
        if len(features) != 50:
            raise ValueError(f"Feature vector length is {len(features)}, expected 50.")

        # Predict
        features_scaled = scaler.transform([features])
        prediction = int(model.predict(features_scaled)[0])
        probability = float(model.predict_proba(features_scaled)[0][1])

        return PredictResponse(prediction=prediction, probability_illicit=probability)

    except Exception as e:
        print(f"❌ [PREDICT ERROR]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

