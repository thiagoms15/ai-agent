import os
import sys
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import your local functions
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file

# Load Gemini API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.", file=sys.stderr)
    sys.exit(1)

# Parse CLI arguments
if len(sys.argv) < 2:
    print("Error: Please provide a prompt as a command-line argument.", file=sys.stderr)
    print("Usage: python3 main.py \"Your prompt here\" [--verbose]", file=sys.stderr)
    sys.exit(1)

user_prompt = sys.argv[1]
verbose_output = "--verbose" in sys.argv

# Hardcoded working directory
working_directory = "calculator"

# Function declarations (schemas)
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of a file, up to 10000 characters.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path to the file to read.",
            ),
        },
        required=["file_path"]
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file, creating it if it doesn't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path to the file to write.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"]
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a Python file and returns the output.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path to the Python file to execute.",
            ),
        },
        required=["file_path"]
    ),
)

# Tool list
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

# System prompt with guidance
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Write or overwrite files
- Execute Python files with optional arguments

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# Create user message
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

# Create Gemini client
client = genai.Client(api_key=api_key)

def call_function(function_call_part, verbose=False):
    from google.genai import types

    function_name = function_call_part.name
    function_args = function_call_part.args or {}

    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    # Add working_directory explicitly
    function_args["working_directory"] = "calculator"

    # Function dispatch map
    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file
    }

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    try:
        result = function_map[function_name](**function_args)
    except Exception as e:
        result = f"Error during function execution: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )

try:
    # Generate content (first turn)
    response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[available_functions]
                )
            )

    if hasattr(response, 'function_calls') and response.function_calls:
        for function_call_part in response.function_calls:
            function_call_result = call_function(function_call_part, verbose_output)

            parts = function_call_result.parts
            if not parts or not hasattr(parts[0], "function_response") or not parts[0].function_response.response:
                raise RuntimeError("Fatal: Function response missing or malformed.")

            if verbose_output:
                print(f"-> {parts[0].function_response.response}")

    else:
        print(response.text)

    # Optional verbose output
    if verbose_output:
        print(f"\nUser prompt: \"{user_prompt}\"")
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        else:
            print("Usage metadata not available.")

except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)

