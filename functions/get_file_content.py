import os

def get_file_content(working_directory, file_path):
    try:
        # Normalize paths
        working_directory = os.path.abspath(working_directory)
        file_path = os.path.abspath(os.path.join(working_directory, file_path))

        # Check for directory traversal
        if not file_path.startswith(working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Check if file exists and is a regular file
        if not os.path.isfile(file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if len(content) > 10000:
            truncated_message = f'\n[...File "{file_path}" truncated at 10000 characters]'
            return content[:10000] + truncated_message

        return content

    except Exception as e:
        return f'Error: {str(e)}'
