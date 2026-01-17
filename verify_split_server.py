import requests
import json
import time

URL_BASELINE = "http://localhost:5000/test2/baseline"
URL_ADAPTIVE = "http://localhost:5000/test2/adaptive"

def run_verify():
    print("Verifying Test 2 Split Routes...")
    
    responses = []
    
    # 1. Baseline Phase - Get all pairs
    print(f"\nRequesting Baseline Pairs from {URL_BASELINE}...")
    try:
        r = requests.get(URL_BASELINE, timeout=5)
        r.raise_for_status()
        probes = r.json()
        
        print(f"Received {len(probes)} baseline probes.")
        assert len(probes) == 4, f"Expected 4 baseline trials, got {len(probes)}"
        
        # Simulate completing them
        for i, probe in enumerate(probes):
            print(f"  Doing baseline {i+1}: {probe['text_word']}")
            responses.append({
                "text_word": probe["text_word"],
                "selected": probe["options"][0],
                "correct": True,
                "reaction_time": 0.8
            })
            
    except Exception as e:
        print(f"FAILED BASELINE: {e}")
        return

    # 2. Adaptive Phase
    print(f"\nRequesting Adaptive Trial from {URL_ADAPTIVE}...")
    try:
        r = requests.post(URL_ADAPTIVE, json={"responses": responses}, timeout=5)
        r.raise_for_status()
        data = r.json()
        
        print(f"Received: {data}")
        assert "text_word" in data, "Missing text_word"
        assert "options" in data, "Missing options"
        assert "analysis" in data, "Missing analysis"
        
    except Exception as e:
        print(f"FAILED ADAPTIVE: {e}")
        return

    print("\nSUCCESS: Split server routes behave as expected.")

if __name__ == "__main__":
    run_verify()
