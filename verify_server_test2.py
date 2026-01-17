import requests
import json
import time

URL = "http://localhost:5000/test2/trial"

def run_verify():
    print("Verifying /test2/trial route...")
    
    responses = []
    
    # 1. Baseline Phase (first 4 trials)
    for i in range(4):
        print(f"\nRequesting Baseline Trial {i+1}...")
        try:
            r = requests.post(URL, json={"responses": responses}, timeout=5)
            r.raise_for_status()
            data = r.json()
            
            print(f"Received: {data}")
            assert data["phase"] == "baseline", f"Expected baseline phase, got {data.get('phase')}"
            assert "text_word" in data, "Missing text_word"
            assert "audio_url" not in data, "Found audio_url but expected none!"
            
            # Simulate response
            responses.append({
                "text_word": data["text_word"],
                "selected": data["options"][0], 
                "correct": True,
                "reaction_time": 1.0
            })
            
        except Exception as e:
            print(f"FAILED: {e}")
            return

    # 2. Adaptive Phase
    print("\nRequesting Adaptive Trial 5...")
    try:
        r = requests.post(URL, json={"responses": responses}, timeout=5)
        r.raise_for_status()
        data = r.json()
        
        print(f"Received: {data}")
        assert data["phase"] == "adaptive", f"Expected adaptive phase, got {data.get('phase')}"
        assert "text_word" in data, "Missing text_word"
        
    except Exception as e:
        print(f"FAILED: {e}")
        return

    print("\nSUCCESS: Server route behaves as expected.")

if __name__ == "__main__":
    # We assume server is running. If not, this script fails.
    # In this environment, we should try to start it or assume the user starts it? 
    # Usually we run the server in background.
    run_verify()
