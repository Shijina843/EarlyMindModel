import pyttsx3
import time
import Levenshtein
import pandas as pd
import joblib
from pathlib import Path
import json
import os

# ---------------- PATHS ----------------
MODEL_PATH = Path("models/logistic_dyslexia.pkl")
SCALER_PATH = Path("models/scaler.pkl")
METADATA_PATH = Path("models/model_metadata.json")

DATA_PATH = Path("data")
AUDIO_PATH = Path("audio")

DATA_PATH.mkdir(exist_ok=True)
AUDIO_PATH.mkdir(exist_ok=True)

OUTPUT_CSV = DATA_PATH / "tts_word_reading_features.csv"

# ---------------- LOAD MODEL ----------------
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

with open(METADATA_PATH) as f:
    metadata = json.load(f)

feature_cols = metadata["features"]

# ---------------- WORD LIST ----------------
words = ["apple", "banana", "orange", "grape", "pineapple"]

# ---------------- TTS FUNCTION ----------------
def speak_and_save(word):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)

    audio_file = AUDIO_PATH / f"{word}.wav"
    engine.save_to_file(word, str(audio_file))
    engine.runAndWait()
    engine.stop()

    time.sleep(0.4)  # ensure file is flushed
    os.system(f'start "" "{audio_file}"')  # Windows playback

# ---------------- TEST START ----------------
print("\n--- Timed Word Reading Test ---")
print("Type the word you hear. Press Enter when done.\n")

data = []

for word in words:
    print("\nListen carefully...")
    speak_and_save(word)

    input_start = time.time()
    typed_word = input("Type the word: ").strip()
    input_end = time.time()

    # ---------------- FEATURES ----------------
    avg_word_time_ms = (input_end - input_start) * 1000
    reading_speed_wpm = 60000 / max(avg_word_time_ms, 1)
    word_error_rate = Levenshtein.distance(word, typed_word) / max(len(word), 1)

    features = {
        "avg_word_time_ms": avg_word_time_ms,
        "reading_speed_wpm": reading_speed_wpm,
        "word_error_rate": word_error_rate,
        "pause_count": typed_word.count(" "),
        "self_correction_count": 0,
        "reaction_time_ms": 0,
        "phoneme_accuracy": 0.95,
        "confusable_error_rate": 0.05,
        "skipped_trials": 0,
        "repeated_attempts": 0
    }

    # ---------------- PREDICTION ----------------
    X = pd.DataFrame([features])[feature_cols]
    X_scaled = scaler.transform(X)

    pred_class = model.predict(X_scaled)[0]
    pred_prob = model.predict_proba(X_scaled)[0][1]

    label = "High Risk" if pred_class == 1 else "Low Risk"
    print(f"\nPrediction: {label} (Risk Probability: {pred_prob:.2f})")

    features["typed_word"] = typed_word
    features["target_word"] = word
    features["pred_class"] = pred_class
    features["pred_prob"] = pred_prob

    data.append(features)

# ---------------- SAVE RESULTS ----------------
df = pd.DataFrame(data)
df.to_csv(OUTPUT_CSV, index=False)

print("Test complete!")
