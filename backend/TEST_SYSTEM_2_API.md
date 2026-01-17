# Test System 2 API Documentation

Test System 2 is a text-only, adaptive reading assessment system. It consists of two phases: **Baseline** (fixed/shuffled) and **Adaptive** (dynamic generation).

## Base URL
```
http://localhost:5000
```
## Overview
- **Text-Only**: No audio files or URLs are returned.
- **Split Routes**: Separate endpoints for fetching baseline trials and generating adaptive trials.

---

## 1. Get Baseline Trials
Fetches the initial set of 4 baseline word pairs.

- **URL**: `/test2/baseline`
- **Method**: `GET`
- **Response**: Array of trial objects.

### Response Example
```json
[
  {
    "text_word": "win",
    "options": ["wen", "win"],
    "correct_index": 1
  },
  {
    "text_word": "sup",
    "options": ["sup", "sub"],
    "correct_index": 0
  },
  {
    "text_word": "log",
    "options": ["log", "fog"],
    "correct_index": 0
  },
  {
    "text_word": "map",
    "options": ["map", "nap"],
    "correct_index": 0
  }
]
```

---

## 2. Get Adaptive Trial
Generates the next single adaptive trial based on the user's performance history.

- **URL**: `/test2/adaptive`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**: JSON object containing user response history.

### Request Body Schema
| Field | Type | Description |
|---|---|---|
| `responses` | Array | List of all previous trial results (baseline + adaptive). |

**Response Item Schema (Input):**
| Field | Type | Description |
|---|---|---|
| `text_word` | String | The target word shown in text (e.g., "win"). |
| `selected` | String | The option the user selected. |
| `correct` | Boolean | Whether the selection was correct. |
| `reaction_time` | Float | Time taken in seconds. |

### Request Example
```json
{
  "responses": [
    {
      "text_word": "win",
      "selected": "wen",
      "correct": false,
      "reaction_time": 1.5
    },
    {
      "text_word": "sup",
      "selected": "sup",
      "correct": true,
      "reaction_time": 0.8
    }
    // ... include all previous responses
  ]
}
```

### Response Example
Returns a single object for the next trial.

```json
{
  "text_word": "bubble",
  "options": ["bubble", "buddle"],
  "correct_index": 0,
  "analysis": "suspected phonological" 
}
```
*Note: `analysis` field provides the current risk assessment.*

---

## Workflow Example
1. **Start**: Call `GET /test2/baseline`. Receive 4 trials.
2. **Execute**: Present trials 1-4 to the user. Collect results.
3. **Adaptive Loop**:
   - Send results of 1-4 to `POST /test2/adaptive`. Receive Trial 5.
   - User does Trial 5.
   - Send results of 1-5 to `POST /test2/adaptive`. Receive Trial 6.
   - Repeat until max trials (10) reached.
