import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.", file=sys.stderr)
    sys.exit(1)

# Parse input
if len(sys.argv) < 2:
    print("Usage: python3 main.py \"your prompt here\" [--verbose]", file=sys.stderr)
    sys.exit(1)

user_prompt = sys.argv[1]
verbose = "--verbose" in sys.argv
working_directory = "calculator"

# ---- Function Schemas ----
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a directory with sizes, constrained to working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory to list files from, relative to working directory."
            )
        }
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads a file up to 10,000 characters.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Relative path to file."
            )
        },
        required=["file_path"]
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(type=types.Type.STRING, description="Relative path to file."),
            "content": types.Schema(type=types.Type.STRING, description="Content to write.")
        },
        required=["file_path", "content"]
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file and returns its output.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Relative path to Python file to run."
            )
        },
        required=["file_path"]
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)

# ---- Function Caller ----
def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = function_call_part.args or {}
    args["working_directory"] = working_directory

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

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
                    response={"error": f"Unknown function: {function_name}"}
                )
            ]
        )

    try:
        result = function_map[function_name](**args)
    except Exception as e:
        result = f"Error during function execution: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result}
            )
        ]
    )

# ---- Agent System Prompt ----
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Write or overwrite files
- Execute Python files

All paths should be relative to the working directory. You do not need to specify the working directory—it is automatically added.
"""

# ---- Main agent loop ----
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)])
]

client = genai.Client(api_key=api_key)

for i in range(20):
    if verbose:
        print(f"\n=== Iteration {i + 1} ===")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[available_functions]
        )
    )

    # Add all candidates' content to history
    if hasattr(response, "candidates"):
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

    # If a function is called, handle it
    if hasattr(response, "function_calls") and response.function_calls:
        for function_call_part in response.function_calls:
            function_result = call_function(function_call_part, verbose)

            # Add the function result to the messages
            messages.append(function_result)

            if verbose:
                result_data = function_result.parts[0].function_response.response
                print(f"-> {result_data}")
    else:
        # No function called = final response
        print("\nFinal response:\n")
        print(response.text)
        break
else:
    print("\nStopped after 20 iterations (max reached).")

