import random
import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "conclave-ai"

FALLBACK_WORDS = ["bear", "pear", "deal", "real", "fan", "van"]

def generate_pair(prompt_hints, exclude_words=None):
    if exclude_words is None:
        exclude_words = []
    
    target_phonemes = prompt_hints.get("target_phonemes", [])
    
    # Simple fallback if no specific phoneme target (e.g. fluency/attention risk only)
    if not target_phonemes:
        target_phonemes = ["b", "p"] # default to common confusers

    prompt = f"""
Task: Generate ONE simple word for a reading test.
Constraints:
- Must contain one of these letters: {', '.join(target_phonemes)}
- Word length: 3-5 letters
- Child-friendly
- NO punctuation
- Do NOT use: {', '.join(exclude_words)}
Output ONLY the word.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.8}
            },
            timeout=3
        )
        data = response.json()
        raw_word = data.get("response", "").strip().lower()
        word = re.sub(r'[^\w]', '', raw_word)
        
        if not word or word in exclude_words:
            raise ValueError("Invalid word generated")

    except Exception as e:
        print(f"Gen error: {e}. Using fallback.")
        available = [w for w in FALLBACK_WORDS if w not in exclude_words]
        word = random.choice(available) if available else "cat"

    # Create a distractor
    # Quick heuristic: change 1 letter to make a distractor 
    # (or use a rhyme if we had a phonetic dictionary, here we fake it)
    if len(word) > 1:
        distractor = word[:-1] + ("z" if word[-1] != "z" else "s") # dumb distractor
        # Try to make a better distractor if it's a known pattern
        if word.startswith("b"): distractor = "d" + word[1:]
        elif word.startswith("d"): distractor = "b" + word[1:]
        elif word.startswith("p"): distractor = "q" + word[1:]
        elif word.startswith("q"): distractor = "p" + word[1:]
    else:
        distractor = "x"

    options = [word, distractor]
    random.shuffle(options)

    return {
        "audio_word": word,
        "options": options,
        "correct_index": options.index(word)
    }
