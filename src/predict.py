import pandas as pd
import joblib
import json
from pathlib import Path

# Paths
MODEL_PATH = Path("models/logistic_dyslexia.pkl")
SCALER_PATH = Path("models/scaler.pkl")
METADATA_PATH = Path("models/model_metadata.json")
DATA_CSV = Path("data/tts_word_reading_features.csv")

# Load model and scaler
print("Loading model and scaler...")
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
print("Model loaded successfully.\n")

# Load feature order
with open(METADATA_PATH) as f:
    metadata = json.load(f)
feature_cols = metadata['features']

# Load new data
print(f"Loading features from {DATA_CSV}...")
df = pd.read_csv(DATA_CSV)

# Select features in exact order
X = df[feature_cols]

# Scale features
X_scaled = scaler.transform(X)

# Predict
pred_class = model.predict(X_scaled)
pred_prob = model.predict_proba(X_scaled)[:,1]

# Add results to dataframe
df["pred_class"] = pred_class
df["pred_prob"] = pred_prob
df["label"] = ["High Risk" if c==1 else "Low Risk" for c in pred_class]

print("\nPredictions:")
print(df[["target_word","typed_word","pred_class","pred_prob","label"]])

# Save predictions
df.to_csv("data/tts_word_reading_predictions.csv", index=False)
print("\nPredictions saved to data/tts_word_reading_predictions.csv")
