import time
import requests
from .baseline import BASELINE_PAIRS
from .generator import generate_pair
from .logic import analyze_responses
from .prompt_builder import build_prompt

MAX_TRIALS = 10
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "conclave-ai"


def simulate_user_choice(pair):
    """
    Replace this with UI input.
    Here we simulate imperfect user behavior.
    """
    import random
    time.sleep(random.uniform(0.8, 2.2))
    if random.random() < 0.75:
        return pair["correct_index"]
    return 1 - pair["correct_index"]


def generate_adaptive_question(prompt_hints):
    """
    Uses prompt_hints → builds prompt → calls LLM
    """
    prompt = build_prompt(prompt_hints)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def run_test():
    responses = []

    print("\n--- Phase 1: Baseline ---\n")

    for pair in BASELINE_PAIRS:
        start = time.time()
        choice = simulate_user_choice(pair)
        rt = time.time() - start

        responses.append({
            "audio": pair["audio"],
            "selected": pair["options"][choice],
            "correct": choice == pair["correct_index"],
            "reaction_time": round(rt, 2)
        })

    analysis = analyze_responses(responses)
    print("Baseline analysis:", analysis)

    print("\n--- Phase 2: Adaptive ---\n")

    trials = len(responses)

    # 🔑 THIS replaces fragile string logic
    prompt_hints = analysis["prompt_hints"]
    assessment = analysis["assessment"]
    print("Prompt hints:", prompt_hints,"Assessment:", assessment)
    while trials < MAX_TRIALS and "suspected" in assessment:
        # ---- OPTION A: GenAI-driven adaptive task ----
        adaptive_question = generate_adaptive_question(prompt_hints)

        # For now, still convert to pair-based task (hybrid approach)
        pair = generate_pair(prompt_hints)
        print("Pair",pair)
        start = time.time()
        choice = simulate_user_choice(pair)
        rt = time.time() - start

        responses.append({
            "audio": pair["audio_word"],
            "selected": pair["options"][choice],
            "correct": choice == pair["correct_index"],
            "reaction_time": round(rt, 2)
        })

        trials += 1

        # 🔁 Re-analyze after each adaptive trial
        analysis = analyze_responses(responses)
        assessment = analysis["assessment"]
        prompt_hints = analysis["prompt_hints"]

        print("Adaptive step →", assessment)

    print("\n--- Final Results ---\n")
    final = analyze_responses(responses)
    print(final)

    print("\nDetailed responses:")
    for r in responses:
        print(r)


if __name__ == "__main__":
    run_test()
