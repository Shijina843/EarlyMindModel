def build_prompt(prompt_hints, task_type="reading"):
    phonemes = prompt_hints.get("target_phonemes", [])
    task_length = prompt_hints.get("task_length", "normal")
    difficulty = prompt_hints.get("difficulty", "normal")

    # map task length to word count
    if task_length == "short":
        word_range = "5 to 6"
    else:
        word_range = "6 to 8"

    # base prompt
    prompt = f"""
Task: Generate a child-friendly reading task.

Constraints:
- Word count: {word_range}
- Vocabulary difficulty: {difficulty}
"""

    # add phoneme focus only if present
    if phonemes:
        phoneme_str = ", ".join(phonemes)
        prompt += f"- Emphasize letters: {phoneme_str}\n"

    prompt += """
- No punctuation
- Avoid rare words

Output only the sentence.
"""

    return prompt.strip()
