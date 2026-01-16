import pyttsx3
import os

print("Starting TTS debug...")
try:
    engine = pyttsx3.init()
    print("Engine initialized.")
    filepath = "test_audio.wav"
    engine.save_to_file("testing", filepath)
    print("Saving to file...")
    engine.runAndWait()
    print("Run loop finished.")
    if os.path.exists(filepath):
        print(f"File created: {filepath}, size: {os.path.getsize(filepath)} bytes")
    else:
        print("File NOT created.")
except Exception as e:
    print(f"Error: {e}")
