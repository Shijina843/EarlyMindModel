import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Paths
DATA_PATH = Path("data/synthetic_dyslexia.csv")
MODEL_PATH = Path("models")
MODEL_PATH.mkdir(exist_ok=True)

MODEL_FILE = MODEL_PATH / "logistic_dyslexia.pkl"

def main():
    # ---------------------------
    # 1. Load dataset
    # ---------------------------
    df = pd.read_csv(DATA_PATH)
    print("Dataset loaded. Shape:", df.shape)

    # Features & Labels
    X = df.drop("label", axis=1)
    y = df["label"]

    # ---------------------------
    # 2. Train-test split
    # ---------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("Train/Test split done:", X_train.shape, X_test.shape)

    # ---------------------------
    # 3. Standardize features
    # ---------------------------
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler for later use
    joblib.dump(scaler, MODEL_PATH / "scaler.pkl")

    # ---------------------------
    # 4. Train Logistic Regression
    # ---------------------------
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_scaled, y_train)

    # ---------------------------
    # 5. Evaluate model
    # ---------------------------
    y_pred = model.predict(X_test_scaled)

    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

    # ---------------------------
    # 6. Save trained model
    # ---------------------------
    joblib.dump(model, MODEL_FILE)
    print(f"\nModel saved successfully at {MODEL_FILE}")

if __name__ == "__main__":
    main()
