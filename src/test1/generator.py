import random
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "conclave-ai"

# Static fallback pairs (last-resort only)
FALLBACKS = {
    "b/d": {
        "audio_word": "bed",
        "options": ["bed", "ded"],
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

def generate_pair(prompt_hints):
    """
    Generates a minimal-pair task using GenAI.
    Falls back to static pairs if generation fails.
    """

    focus = infer_focus(prompt_hints)

    # ---- Build prompt ----
    prompt = f"""
Task: Generate ONE simple word for a sound-matching test.

Constraints:
- Focus phonemes: {focus.replace('/', ' and ')}
- Word length: 3 to 4 letters
- Child-friendly word
- No punctuation
- Output ONLY the word
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=5
        )

        data = response.json()

        if "response" not in data:
            raise ValueError("Invalid LLM response")

        word = data["response"].strip().lower()

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
        return FALLBACKS[focus]
