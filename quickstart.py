""" 

Make your first request
Here is an example that uses the generateContent method to send a request to the Gemini API using the Gemini 2.5 Flash model.

If you set your API key as the environment variable GEMINI_API_KEY, it will be picked up automatically by the client when using the Gemini API libraries. Otherwise you will need to pass your API key as an argument when initializing the client.

Note that all code samples in the Gemini API docs assume that you have set the environment variable GEMINI_API_KEY.

"""

from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)
