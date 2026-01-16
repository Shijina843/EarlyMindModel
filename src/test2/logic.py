import statistics

SUSPECT_THRESHOLD = 0.5
LOW_RISK_THRESHOLD = 0.35

def analyze_responses(responses):
    if not responses:
        return {
            "accuracy": 0.0,
            "avg_rt": 0.0,
            "var_rt": 0.0,
            "risk_scores": {"phonological": 0.0, "fluency": 0.0, "attention": 0.0},
            "assessment": "insufficient data",
            "prompt_hints": {}
        }

    accuracy = sum(r["correct"] for r in responses) / len(responses)
    reaction_times = [r["reaction_time"] for r in responses]
    avg_rt = statistics.mean(reaction_times)
    var_rt = statistics.pvariance(reaction_times) if len(reaction_times) > 1 else 0.0

    # Custom logic for "zconditions" (risk factors)
    # Using similar heuristic as test1 for now
    scores = {
        "phonological": 0.0,
        "fluency": 0.0,
        "attention": 0.0
    }

    # Phonological checks (e.g., error on similarity)
    # Here we assume specific pairs target p/b/d confusability
    phoneme_errors = sum(
        1 for r in responses
        if not r["correct"] # Simplified check compared to test1 which checked specific audio words
    )
    
    if phoneme_errors >= 1: # stricter for "pinpointing"
         scores["phonological"] += 0.5 * phoneme_errors

    # Fluency checks
    if avg_rt > 1.5:
        scores["fluency"] += 0.4
    if accuracy >= 0.9 and avg_rt > 1.8: # high accuracy but slow
        scores["fluency"] += 0.3

    # Attention checks
    if var_rt > 0.4:
        scores["attention"] += 0.5

    # Normalize max score to 1.0 for now for safety
    for k in scores:
        scores[k] = min(scores[k], 1.0)

    # Determine hints for next generation
    # logic: push towards the highest risk area to "pinpoint" it
    max_risk = max(scores.values())
    primary_risk = max(scores, key=scores.get) if max_risk > 0 else None

    prompt_hints = {
        "target_phonemes": [],
        "difficulty": "normal"
    }

    if primary_risk == "phonological":
        # Pinpoint phonological: generate similar sounding words
        prompt_hints["target_phonemes"] = ["b", "d", "p", "q"] # broadened for test2
    elif primary_risk == "fluency":
        prompt_hints["difficulty"] = "hard" # challenge fluency with harder words? or easy to verify speed? Let's go harder.
    elif primary_risk == "attention":
         prompt_hints["difficulty"] = "variable" # not used yet but concept for generator

    # Assessment String
    if max_risk < LOW_RISK_THRESHOLD:
        label = "no significant issue detected"
    else:
        label = f"suspected {primary_risk}"

    return {
        "accuracy": round(accuracy, 2),
        "avg_rt": round(avg_rt, 2),
        "var_rt": round(var_rt, 2),
        "risk_scores": scores,
        "assessment": label,
        "prompt_hints": prompt_hints
    }
