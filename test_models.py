import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

models_to_test = [
    "gemini/gemini-2.5-flash",
    "gemini/gemini-2.0-flash",
    "gemini/gemini-1.5-flash-latest",
    "gemini/gemini-1.5-flash-001",
    "gemini/gemini-1.5-pro",
]

for m in models_to_test:
    print(f"Testing {m}...")
    try:
        response = completion(model=m, messages=[{"role": "user", "content": "reply with OK"}])
        print(f"✅ SUCCESS: {m}")
        break  # We found a working one!
    except Exception as e:
        print(f"❌ FAILED: {m} -> {e}")
