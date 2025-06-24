import os

def get_files_info(working_directory, directory=None):
    try:
        if directory is None:
            directory = working_directory

        # Get absolute paths
        working_directory = os.path.abspath(working_directory)
        directory = os.path.abspath(os.path.join(working_directory, directory))

        # Check if directory is within working_directory
        if not directory.startswith(working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Check if it's a directory
        if not os.path.isdir(directory):
            return f'Error: "{directory}" is not a directory'

        result_lines = []
        for entry in os.scandir(directory):
            try:
                size = entry.stat().st_size
                is_dir = entry.is_dir()
                result_lines.append(f'- {entry.name}: file_size={size} bytes, is_dir={is_dir}')
            except Exception as e:
                result_lines.append(f'- {entry.name}: Error: {str(e)}')

        return '\n'.join(result_lines)

    except Exception as e:
        return f'Error: {str(e)}'

