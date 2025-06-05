# === File: backend/models.py ===
from sqlalchemy import Column, Integer, String, Float
from db import Base

class UserFeatures(Base):
    __tablename__ = 'user_features'

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    features = Column(String)  # store features as a comma-separated string
    prediction = Column(Integer)

class AuthUser(Base):
    __tablename__ = 'auth_users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)