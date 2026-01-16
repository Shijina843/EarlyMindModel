import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the src directory to sys.path so we can import from test1
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from test1.baseline import BASELINE_PAIRS
from test1.logic import analyze_responses
from test1.generator import generate_pair

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/baseline', methods=['GET'])
def get_baseline():
    """Returns the baseline pairs for the initial phase."""
    # We might want to randomize the order or just return them as is.
    # The requirement says "without reducing repetitions in consecutive api calls"
    # interpreting this as just returning the standard list is safest for now,
    # or the user might mean we *shouldn't* shuffle?
    # Actually, "without reducing repetitions" might be a typo for "without inducing repetitions".
    # But usually a baseline is a fixed set. Let's return the fixed set.
    return jsonify(BASELINE_PAIRS)

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
    
    # Generate the next pair using the logic from generator.py
    # We pass the prompt hints derived from the analysis
    new_pair = generate_pair(prompt_hints)
    
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
