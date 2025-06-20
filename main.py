import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.", file=sys.stderr)
    sys.exit(1)

if len(sys.argv) < 2:
    print("Error: Please provide a prompt as a command-line argument.", file=sys.stderr)
    print("Usage: python3 main.py \"Your prompt here\" [--verbose]", file=sys.stderr)
    sys.exit(1)

user_prompt = sys.argv[1]
verbose_output = False

if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
    verbose_output = True

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=messages,
    )

    print(response.text)

    if verbose_output:
        print(f"User prompt: \"{user_prompt}\"")
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        else:
            print("Usage metadata not available in the response for token counts.")

except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)
