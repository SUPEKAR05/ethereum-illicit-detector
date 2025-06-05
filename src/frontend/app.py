# === File: frontend/app.py ===
import streamlit as st
import requests

st.title("Ethereum Illicit Account Detector")

page = st.sidebar.selectbox("Navigation", ["Login", "Signup", "Check Address"])

backend_url = "http://localhost:8000"

if page == "Signup":
    st.subheader("Create Account")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        try:
            res = requests.post(f"{backend_url}/signup", json={"username": username, "email": email, "password": password})
            if res.status_code == 200:
                st.success("Signup successful!")
            else:
                st.error(res.json().get("detail", "Signup failed."))
        except Exception as e:
            st.error(f"Request failed: {e}")

elif page == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            res = requests.post(f"{backend_url}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state.username = username
                st.success("Login successful!")
            else:
                st.error(res.json().get("detail", "Login failed."))
        except Exception as e:
            st.error(f"Login request failed: {e}")

elif page == "Check Address":
    if "username" not in st.session_state:
        st.warning("Please log in first.")
    else:
        st.subheader("Check Ethereum Address")
        address = st.text_input("Enter Ethereum Address")
        if st.button("Check Account"):
            try:
                res = requests.post(f"{backend_url}/predict", json={"address": address})
                res.raise_for_status()
                result = res.json()
                st.success(f"Prediction: {'Illicit 🚨' if result['prediction'] == 1 else 'Normal ✅'}")
                st.info(f"Probability of Illicit Activity: {result['probability_illicit']*100:.2f}%")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
            except ValueError:
                st.error("Server response could not be decoded. Please check backend logs.")
