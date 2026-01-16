import statistics

SUSPECT_THRESHOLD = 0.5
LOW_RISK_THRESHOLD = 0.35

def analyze_responses(responses):
    accuracy = sum(r["correct"] for r in responses) / len(responses)

    reaction_times = [r["reaction_time"] for r in responses]
    avg_rt = statistics.mean(reaction_times)
    var_rt = statistics.pvariance(reaction_times)

    phoneme_errors = sum(
        1 for r in responses
        if not r["correct"] and r["audio"] in ["bed", "bad", "dad"]
    )

    scores = {
        "phonological": 0.0,
        "fluency": 0.0,
        "attention": 0.0
    }

    # phonological
    if phoneme_errors >= 2:
        scores["phonological"] += 0.5
    if accuracy < 0.8:
        scores["phonological"] += 0.3

    # fluency
    if avg_rt > 1.6:
        scores["fluency"] += 0.4
    if accuracy >= 0.85 and avg_rt > 1.8:
        scores["fluency"] += 0.3

    # attention
    if var_rt > 0.5:
        scores["attention"] += 0.5
    if var_rt > 0.8:
        scores["attention"] += 0.2

    issues = []

    if scores["phonological"] >= SUSPECT_THRESHOLD:
        issues.append("phonological (b/d risk)")
    if scores["fluency"] >= SUSPECT_THRESHOLD:
        issues.append("reading fluency risk")
    if scores["attention"] >= SUSPECT_THRESHOLD:
        issues.append("attention instability")

    if max(scores.values()) < LOW_RISK_THRESHOLD:
        label = "no significant issue detected"
    elif len(issues) == 1:
        label = f"suspected {issues[0]}"
    else:
        label = "multiple suspected issues detected"

    prompt_hints = {
        "target_phonemes": ["b", "d"] if scores["phonological"] >= 0.5 else [],
        "task_length": "short" if scores["attention"] >= 0.5 else "normal",
        "difficulty": "easy" if scores["fluency"] >= 0.5 else "normal"
    }

    return {
        "accuracy": round(accuracy, 2),
        "avg_rt": round(avg_rt, 2),
        "var_rt": round(var_rt, 2),
        "risk_scores": scores,
        "assessment": label,
        "prompt_hints": prompt_hints
    }
