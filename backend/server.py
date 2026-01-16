import sys
import os
import time
from gtts import gTTS
from flask import Flask, jsonify, request, url_for
from flask_cors import CORS

# Add the src directory to sys.path so we can import from test1
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from test1.baseline import BASELINE_PAIRS
from test1.logic import analyze_responses
from test1.generator import generate_pair

from test2.baseline import BASELINE_PAIRS as BASELINE_PAIRS_2
from test2.logic import analyze_responses as analyze_responses_2
from test2.generator import generate_pair as generate_pair_2

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_audio_file(word):
    """
    Generates an audio file for the given word using gTTS if it doesn't exist.
    Returns the filename.
    """
    # gTTS saves as mp3 usually, but we can name it whatever. mp3 is standard.
    filename = f"{word}.mp3" 
    filepath = os.path.join(AUDIO_DIR, filename)
    
    if not os.path.exists(filepath):
        try:
            tts = gTTS(text=word, lang='en')
            tts.save(filepath)
            print(f"Generated audio for: {word}")
        except Exception as e:
            print(f"Error generating audio for {word}: {e}")
            
    return filename

def add_audio_url(pair):
    """
    Helper to add audio URL to a pair.
    """
    word = pair.get('audio', pair.get('audio_word'))
    if word:
        filename = generate_audio_file(word)
        # Construct full URL or relative path.
        try:
            pair['audio_url'] = url_for('static', filename=f'audio/{filename}', _external=True)
        except RuntimeError:
            pair['audio_url'] = f'/static/audio/{filename}'
    return pair

@app.route('/baseline', methods=['GET'])
def get_baseline():
    """Returns the baseline pairs for the initial phase."""
    # We copy the list to avoid modifying the original global constant if we were holding it in memory statefully
    # (though imports usually cache, modifying dicts inside list is side-effecty).
    pairs = []
    for p in BASELINE_PAIRS:
        # Create a deep-ish copy of the dict and options list so we can shuffle safely
        pair_copy = p.copy()
        if "options" in pair_copy:
            pair_copy["options"] = list(pair_copy["options"]) # Copy list
            
            # Shuffle options
            import random
            random.shuffle(pair_copy["options"])
            
            # Re-calculate correct_index because shuffling changed positions
            # The baseline pairs in baseline.py use "audio" as the target word key
            target = pair_copy["audio"]
            if target in pair_copy["options"]:
                pair_copy["correct_index"] = pair_copy["options"].index(target)
            else:
                # Fallback if audio word not in options (shouldn't happen with well-formed data)
                # But looking at baseline.py: "audio": "bed", "options": ["bed", "ded"]
                pass 
        
        pairs.append(pair_copy)
        
    # Shuffle the order of the pairs themselves so the first word isn't always the same
    import random
    random.shuffle(pairs)
        
    for pair in pairs:
        add_audio_url(pair)
    return jsonify(pairs)

@app.route('/next-trial', methods=['POST'])
def next_trial():
    """
    Expects JSON body:
    {
        "responses": [
            { "audio": "bed", "selected": "ded", "correct": false, "reaction_time": 1.2 },
            ...
        ]
    }
    Returns a new pair based on analysis.
    """
    data = request.json
    if not data or 'responses' not in data:
        return jsonify({"error": "Missing 'responses' field"}), 400

    responses = data['responses']
    
    # Analyze the responses so far
    analysis = analyze_responses(responses)
    prompt_hints = analysis["prompt_hints"]
    assessment = analysis["assessment"]
    
    # Collect used words (baseline + history)
    # 1. From baseline
    used_words = set(p["audio"] for p in BASELINE_PAIRS)
    # 2. From history
    for r in responses:
        if "audio" in r:
            used_words.add(r["audio"])
    
    # Generate the next pair using the logic from generator.py
    # We pass the prompt hints derived from the analysis and the exclusion list
    new_pair = generate_pair(prompt_hints, exclude_words=list(used_words))
    
    # Add audio URL
    add_audio_url(new_pair)
    
    # We include the assessment in the response for debugging/frontend info if needed
    result = {
        "next_trial": new_pair,
        "analysis": {
            "assessment": assessment,
            "prompt_hints": prompt_hints,
            "stats": {
                "accuracy": analysis["accuracy"],
                "avg_rt": analysis["avg_rt"]
            }
        }
    }
    
    return jsonify(result)

@app.route('/test2/baseline', methods=['GET'])
def test2_baseline():
    """
    Returns all baseline pairs for Test 2.
    Response format: JSON list of pairs (text-only).
    """
    pairs = []
    # We copy info from BASELINE_PAIRS_2
    for p in BASELINE_PAIRS_2:
        pair = p.copy()
        # Shuffle options
        import random
        options = list(pair["options"])
        random.shuffle(options)
        pair["options"] = options
        
        # Re-calc correct index
        if pair["audio"] in options:
            pair["correct_index"] = options.index(pair["audio"])
            
        # Structure for client
        pairs.append({
            "text_word": pair["audio"], 
            "options": pair["options"],
            "correct_index": pair["correct_index"]
        })
    
    # Shuffle the pairs order? Or keep order? 
    # Test 1 shuffled pairs. Let's shuffle pairs.
    import random
    random.shuffle(pairs)
    
    return jsonify(pairs)

@app.route('/test2/adaptive', methods=['POST'])
def test2_adaptive():
    """
    Generates ONE adaptive trial for Test 2 based on history.
    Response format: JSON object (text-only).
    """
    data = request.json
    responses = data.get('responses', []) if data else []
    
    analysis = analyze_responses_2(responses)
    prompt_hints = analysis["prompt_hints"]
    
    # Exclude words already used
    exclude = set()
    for r in responses:
         word = r.get("text_word", r.get("audio"))
         if word:
             exclude.add(word)
    
    # Generate new pair
    pair = generate_pair_2(prompt_hints, exclude_words=list(exclude))
    
    return jsonify({
        "text_word": pair["audio_word"], 
        "options": pair["options"],
        "correct_index": pair["correct_index"],
        "analysis": analysis["assessment"]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
