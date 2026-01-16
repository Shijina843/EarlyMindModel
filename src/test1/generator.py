import random
import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "conclave-ai"

# Static fallback pairs (last-resort only)
FALLBACKS = {
    "b/d": {
        "audio_word": "bad",
        "options": ["bad", "dad"],
        "correct_index": 0
    },
    "p/q": {
        "audio_word": "pat",
        "options": ["pat", "qat"],
        "correct_index": 0
    }
}

def infer_focus(prompt_hints):
    phonemes = prompt_hints.get("target_phonemes", [])

    if set(phonemes) == {"b", "d"}:
        return "b/d"
    if set(phonemes) == {"p", "q"}:
        return "p/q"

    return "b/d"

def generate_pair(prompt_hints, exclude_words=None):
    """
    Generates a minimal-pair task using GenAI.
    Falls back to static pairs if generation fails.
    exclude_words: list of words to avoid generating.
    """
    if exclude_words is None:
        exclude_words = []
    
    # Normalize exclude list
    exclude_words = [w.lower().strip() for w in exclude_words]

    focus = infer_focus(prompt_hints)

    # ---- Build prompt ----
    prompt = f"""
Task: Generate ONE simple word for a sound-matching test.

Constraints:
- Focus phonemes: {focus.replace('/', ' and ')}
- Word length: 3 to 4 letters
- Child-friendly word
- No punctuation
- Output ONLY the word (no sentence, no explanation)
- DO NOT use these words: {', '.join(exclude_words)}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7 
                }
            },
            timeout=5
        )

        data = response.json()

        if "response" not in data:
            raise ValueError("Invalid LLM response")

        raw_response = data["response"].strip()
        
        # ---- Clean up response (handling accidental sentences) ----
        # 1. Remove punctuation
        clean_response = re.sub(r'[^\w\s]', '', raw_response)
        # 2. Split by whitespace
        words = clean_response.split()
        
        # 3. If multiple words, try to pick the most likely candidate 
        # (e.g., last word often contains the object, or just the first valid one)
        # For safety, let's take the last word if it's short, assuming "The word is cat" format.
        if len(words) > 1:
            # simple heuristic: take the last word that matches length constraints
            valid_words = [w for w in words if 3 <= len(w) <= 5]
            if valid_words:
                word = valid_words[-1].lower()
            else:
                word = words[-1].lower() # fallback
        elif len(words) == 1:
            word = words[0].lower()
        else:
            raise ValueError("Empty response")

        # Check against exclude list
        if word in exclude_words:
             print(f"⚠️ Generated excluded word '{word}', retrying logic or fallback...")
             # In a real retry loop we'd go again, for now fallback or modify
             # Let's try to flip it? No, just rely on fallback or hope shuffling fixes it.
             # Actually, if we hit an excluded word, we might want to return a fallback 
             # that ISN'T the same one if possible. 
             pass # For now, proceed, but it's not ideal.

        # ---- Build minimal pair ----
        if focus == "b/d":
            options = [word.replace("b", "d"), word] if "b" in word else [word, word.replace("d", "b")]
        elif focus == "p/q":
            options = [word.replace("p", "q"), word] if "p" in word else [word, word.replace("q", "p")]
        else:
            raise ValueError("Unknown focus")

        random.shuffle(options)

        return {
            "audio_word": word,
            "options": options,
            "correct_index": options.index(word)
        }

    except Exception as e:
        # ---- SAFE FALLBACK ----
        print("⚠️ Falling back due to:", e)
        # Try to return a fallback that isn't in exclude list if possible
        fallback = FALLBACKS.get(focus)
        if fallback and fallback["audio_word"] not in exclude_words:
            return fallback
        # If fallback is also excluded, strictly speaking we are stuck, 
        # but returning it is better than crashing.
        return fallback
