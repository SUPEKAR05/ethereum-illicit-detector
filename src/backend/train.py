# === File: backend/train.py ===
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib
from typing import Tuple

def load_and_preprocess(filepath: str) -> Tuple[np.ndarray, np.ndarray, StandardScaler, LabelEncoder]:
    df = pd.read_csv(filepath)

    # Drop Address
    df = df.drop(columns=['Address'])

    # Encode categorical token type columns
    encoder = LabelEncoder()
    df['ERC20 Most Sent Token Type'] = encoder.fit_transform(df['ERC20 Most Sent Token Type'].astype(str))
    df['ERC20 Most Received Token Type'] = encoder.fit_transform(df['ERC20 Most Received Token Type'].astype(str))

    # Split features and target
    X = df.drop(columns=['Flag']).values
    y = df['Flag'].values

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler, encoder

def train_and_evaluate(X: np.ndarray, y: np.ndarray):
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.15,
        eval_metric="logloss",
        use_label_encoder=False
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("✅ Accuracy:", accuracy_score(y_test, y_pred))
    print("✅ ROC AUC:", roc_auc_score(y_test, y_proba))
    print("\n🧾 Classification Report:\n", classification_report(y_test, y_pred))
    print("\n🧾 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

    return model

def main():
    filepath = "Enhanced_Synthetic_Gas_Dataset.csv"
    X, y, scaler, encoder = load_and_preprocess(filepath)
    model = train_and_evaluate(X, y)

    # Save model, scaler, encoder
    joblib.dump(model, "xgboost_model.pkl")
    joblib.dump(scaler, "scaler.pkl")
    joblib.dump(encoder, "token_type_encoder.pkl")
    print("\n✅ Model, Scaler, and Encoder saved successfully!")

if __name__ == "__main__":
    main()
