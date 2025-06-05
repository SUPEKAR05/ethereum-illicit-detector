# 🛡️ Ethereum Illicit Account Detector

A web-based application that detects whether an Ethereum address is **illicit** or **normal** using real-time features and a trained machine learning model.

---

## 🚀 Features

- 🔐 User Authentication (Signup/Login)
- 🧠 Real-time Ethereum address classification using:
  - On-chain features (transaction counts, gas usage, token transfers, etc.)
  - Synthetic gas behavior modeling
- 📈 ML-powered predictions (XGBoost-based)
- 🌐 Full-stack web app with:
  - **Frontend**: Streamlit
  - **Backend**: FastAPI
  - **Database**: PostgreSQL
- 📦 Model + Scaler stored with `joblib` and used in prediction
- 🔎 Address lookup with live feedback

---
