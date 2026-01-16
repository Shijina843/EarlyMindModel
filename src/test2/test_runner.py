import time
from .baseline import BASELINE_PAIRS
from .logic import analyze_responses
from .generator import generate_pair

MAX_TOTAL_TRIALS = 10
BASELINE_COUNT = 4

def simulate_user_choice(pair):
    # Simulating a user who struggles with 'b' vs 'd' sometimes
    # and has variable speed
    import random
    time.sleep(random.uniform(0.5, 2.0))
    
    word = pair["audio"] if "audio" in pair else pair["audio_word"]
    
    # Introduce error for specific words to test logic
    if word.startswith("b") or word.startswith("d"):
        if random.random() < 0.4: # 40% error rate on b/d
            return 1 - pair["correct_index"]
            
    return pair["correct_index"]

def run_test():
    responses = []
    print(f"Starting Test 2 (Max {MAX_TOTAL_TRIALS} trials)")

    # --- Phase 1: Baseline ---
    print("\n--- Phase 1: Baseline (User Dictated Words) ---")
    for i in range(min(BASELINE_COUNT, len(BASELINE_PAIRS))):
        pair = BASELINE_PAIRS[i]
        print(f"Trial {i+1}: {pair['audio']}")
        
        start = time.time()
        choice = simulate_user_choice(pair)
        rt = time.time() - start
        
        responses.append({
            "audio": pair["audio"],
            "selected": pair["options"][choice],
            "correct": choice == pair["correct_index"],
            "reaction_time": round(rt, 2)
        })

    # --- Phase 2: Adaptive ---
    print("\n--- Phase 2: Adaptive ---")
    
    analysis = analyze_responses(responses)
    print(f"Initial Analysis: {analysis['assessment']}")
    
    while len(responses) < MAX_TOTAL_TRIALS:
        # Check if we have pinpointed enough (stop early concept?)
        # For now, run until max 10 to gather data, or could break if high confidence.
        # The prompt says "first will be 4 baseline... and is max 10 test cases"
        
        prompt_hints = analysis["prompt_hints"]
        exclude = [r["audio"] for r in responses]
        
        pair = generate_pair(prompt_hints, exclude_words=exclude)
        print(f"Trial {len(responses)+1}: {pair['audio_word']} (Hints: {prompt_hints})")
        
        start = time.time()
        choice = simulate_user_choice(pair)
        rt = time.time() - start
        
        responses.append({
            "audio": pair["audio_word"],
            "selected": pair["options"][choice],
            "correct": choice == pair["correct_index"],
            "reaction_time": round(rt, 2)
        })
        
        analysis = analyze_responses(responses)
        print(f"Analysis update: {analysis['assessment']}")

    print("\n--- Final Result ---")
    print(analysis)

if __name__ == "__main__":
    run_test()
