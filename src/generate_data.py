import numpy as np
import pandas as pd
from pathlib import Path

# Reproducibility
np.random.seed(42)

# Output path
DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_PATH / "synthetic_dyslexia.csv"


def generate_low_risk(n):
    """Typical readers"""
    return pd.DataFrame({
        # Timed Word Reading
        "avg_word_time_ms": np.random.normal(450, 80, n),
        "reading_speed_wpm": np.random.normal(150, 20, n),
        "word_error_rate": np.random.uniform(0.0, 0.05, n),
        "pause_count": np.random.poisson(1, n),
        "self_correction_count": np.random.poisson(1, n),

        # Sound–Letter Matching
        "phoneme_accuracy": np.random.uniform(0.90, 1.00, n),
        "confusable_error_rate": np.random.uniform(0.00, 0.10, n),
        "reaction_time_ms": np.random.normal(700, 120, n),
        "skipped_trials": np.random.poisson(0.5, n),
        "repeated_attempts": np.random.poisson(1, n),

        "label": 0  # Low risk
    })


def generate_high_risk(n):
    """Dyslexia-risk patterns"""
    return pd.DataFrame({
        # Timed Word Reading
        "avg_word_time_ms": np.random.normal(1100, 200, n),
        "reading_speed_wpm": np.random.normal(85, 15, n),
        "word_error_rate": np.random.uniform(0.20, 0.50, n),
        "pause_count": np.random.poisson(4, n),
        "self_correction_count": np.random.poisson(3, n),

        # Sound–Letter Matching
        "phoneme_accuracy": np.random.uniform(0.50, 0.80, n),
        "confusable_error_rate": np.random.uniform(0.20, 0.60, n),
        "reaction_time_ms": np.random.normal(1800, 350, n),
        "skipped_trials": np.random.poisson(3, n),
        "repeated_attempts": np.random.poisson(4, n),

        "label": 1  # High risk
    })


def main():
    low_risk = generate_low_risk(500)
    high_risk = generate_high_risk(500)

    df = pd.concat([low_risk, high_risk], ignore_index=True)

    # Clean up invalid values
    df = df.clip(lower=0)

    # Save dataset
    df.to_csv(OUTPUT_FILE, index=False)

    print("Synthetic dataset created successfully!")
    print("Shape:", df.shape)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
