import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import joblib

# Paths
DATA_PATH = Path("data/synthetic_dyslexia.csv")
MODEL_PATH = Path("models")
MODEL_PATH.mkdir(exist_ok=True)

MODEL_FILE = MODEL_PATH / "logistic_dyslexia.pkl"
SCALER_FILE = MODEL_PATH / "scaler.pkl"

def main():
    # Load dataset
    df = pd.read_csv(DATA_PATH)
    
    # Check for missing values
    if df.isnull().sum().sum() > 0:
        df = df.dropna()

    # Features & Labels
    X = df.drop("label", axis=1)
    y = df["label"]

    # ---------------------------
    # Train-test split
    # ---------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("-" * 30)
    print("TRAIN/TEST SPLIT")
    print("-" * 30)
    print(f"Training set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")

    # ---------------------------
    # Standardize features
    # ---------------------------
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    joblib.dump(scaler, SCALER_FILE)

    # ---------------------------
    # Train Logistic Regression
    # ---------------------------
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train_scaled, y_train)

    # ---------------------------
    # Model Evaluation
    # ---------------------------
    print("\n" + "-" * 30)
    print("MODEL EVALUATION")
    print("-" * 30)
    
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    train_acc = model.score(X_train_scaled, y_train)
    test_acc = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"Training Accuracy: {train_acc:.4f}")
    print(f"Test Accuracy: {test_acc:.4f}")
    print(f"ROC-AUC Score: {roc_auc:.4f}")

    # ---------------------------
    # Classification Report
    # ---------------------------
    print("\n" + "-" * 30)
    print("CLASSIFICATION REPORT")
    print("-" * 30)
    print(classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk']))

    # ---------------------------
    # Confusion Matrix
    # ---------------------------
    print("-" * 30)
    print("CONFUSION MATRIX")
    print("-" * 30)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"\nTrue Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
    print(f"False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")

    # ---------------------------
    # Save trained model
    # ---------------------------
    joblib.dump(model, MODEL_FILE)
    
    metadata = {
        'train_accuracy': train_acc,
        'test_accuracy': test_acc,
        'roc_auc': roc_auc,
        'features': list(X.columns),
        'n_samples_train': len(X_train),
        'n_samples_test': len(X_test)
    }
    
    import json
    with open(MODEL_PATH / "model_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    main()