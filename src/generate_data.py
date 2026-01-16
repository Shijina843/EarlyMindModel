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
    """Typical readers with realistic variance"""
    return pd.DataFrame({
        # Timed Word Reading
        "avg_word_time_ms": np.random.normal(550, 180, n),
        "reading_speed_wpm": np.random.normal(140, 35, n),
        "word_error_rate": np.random.uniform(0.0, 0.15, n),
        "pause_count": np.random.poisson(2, n),
        "self_correction_count": np.random.poisson(1.5, n),

        # Sound–Letter Matching
        "phoneme_accuracy": np.random.uniform(0.82, 1.00, n),
        "confusable_error_rate": np.random.uniform(0.00, 0.18, n),
        "reaction_time_ms": np.random.normal(900, 300, n),
        "skipped_trials": np.random.poisson(1, n),
        "repeated_attempts": np.random.poisson(1.5, n),

        "label": 0  # Low risk
    })


def generate_high_risk(n):
    """Dyslexia-risk patterns with realistic variance"""
    return pd.DataFrame({
        # Timed Word Reading
        "avg_word_time_ms": np.random.normal(950, 280, n),
        "reading_speed_wpm": np.random.normal(100, 25, n),
        "word_error_rate": np.random.uniform(0.12, 0.45, n),
        "pause_count": np.random.poisson(3.5, n),
        "self_correction_count": np.random.poisson(2.5, n),

        # Sound–Letter Matching
        "phoneme_accuracy": np.random.uniform(0.60, 0.85, n),
        "confusable_error_rate": np.random.uniform(0.15, 0.55, n),
        "reaction_time_ms": np.random.normal(1500, 400, n),
        "skipped_trials": np.random.poisson(2.5, n),
        "repeated_attempts": np.random.poisson(3.5, n),

        "label": 1  # High risk
    })


def generate_borderline_cases(n):
    """Cases that are harder to classify - mix of both patterns"""
    # Randomly assign true labels
    labels = np.random.choice([0, 1], n)
    
    data = []
    for label in labels:
        if label == 0:  # Low risk with some difficulties
            row = {
                "avg_word_time_ms": np.random.normal(750, 150, 1)[0],
                "reading_speed_wpm": np.random.normal(115, 25, 1)[0],
                "word_error_rate": np.random.uniform(0.10, 0.20, 1)[0],
                "pause_count": np.random.poisson(2.5, 1)[0],
                "self_correction_count": np.random.poisson(2, 1)[0],
                "phoneme_accuracy": np.random.uniform(0.78, 0.90, 1)[0],
                "confusable_error_rate": np.random.uniform(0.12, 0.25, 1)[0],
                "reaction_time_ms": np.random.normal(1150, 250, 1)[0],
                "skipped_trials": np.random.poisson(1.5, 1)[0],
                "repeated_attempts": np.random.poisson(2, 1)[0],
                "label": label
            }
        else:  # High risk with some strengths
            row = {
                "avg_word_time_ms": np.random.normal(800, 180, 1)[0],
                "reading_speed_wpm": np.random.normal(110, 20, 1)[0],
                "word_error_rate": np.random.uniform(0.15, 0.28, 1)[0],
                "pause_count": np.random.poisson(3, 1)[0],
                "self_correction_count": np.random.poisson(2.5, 1)[0],
                "phoneme_accuracy": np.random.uniform(0.70, 0.86, 1)[0],
                "confusable_error_rate": np.random.uniform(0.18, 0.35, 1)[0],
                "reaction_time_ms": np.random.normal(1350, 300, 1)[0],
                "skipped_trials": np.random.poisson(2, 1)[0],
                "repeated_attempts": np.random.poisson(3, 1)[0],
                "label": label
            }
        data.append(row)
    
    return pd.DataFrame(data)


def add_label_noise(df, noise_rate=0.03):
    """Flip labels for a small percentage of cases to simulate real-world mislabeling"""
    n_flip = int(len(df) * noise_rate)
    flip_indices = np.random.choice(df.index, n_flip, replace=False)
    df.loc[flip_indices, 'label'] = 1 - df.loc[flip_indices, 'label']
    return df


def main():
    # Generate different types of cases
    low_risk = generate_low_risk(400)
    high_risk = generate_high_risk(400)
    borderline = generate_borderline_cases(200)  # 20% borderline cases
    
    # Combine all cases
    df = pd.concat([low_risk, high_risk, borderline], ignore_index=True)
    
    # Clean up invalid values
    df = df.clip(lower=0)
    
    # Add small amount of label noise (3%)
    df = add_label_noise(df, noise_rate=0.03)
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save dataset
    df.to_csv(OUTPUT_FILE, index=False)

    print("✓ Synthetic dataset created successfully!")
    print(f"Shape: {df.shape}")
    print(f"Class distribution:\n{df['label'].value_counts()}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()