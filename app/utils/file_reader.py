import os


def get_prompt_from_source(file_path):
    with open(file_path, "r") as file:
        template = file.read()
    return template


# TODO: delete None variants
def create_files(code_snippets, files=None, textData=None):
    """
    Generates files from given code snippets, placing them in specified or default directories.

    Iterates through code snippets to create files with their specified names and extensions. The function 
    looks for matching paths in a provided list of file paths. If a match is found, the file is created in 
    that path; otherwise, it is placed in a '.eng' directory. Directories are created if they don't exist.

    :param code_snippets: List of code snippet objects.
    :param files: String of newline-separated file paths for matching and placing the files.
    :param textData: TextData object.
    :return: None. Outputs status messages for file and directory creation.
    """
    for code_snippet in code_snippets:
        file_name = f"{code_snippet.filename}.{code_snippet.extension}"
        
        project_directory = textData.filepath
        filepathes = files.split("\n")

        matching_paths = [
            path for path in filepathes if os.path.basename(path) == file_name
        ]
        file_path = matching_paths[0] if matching_paths else None

        if file_path != None:
            file_path = join_paths(project_directory, file_path)

            file_directory = os.path.dirname(file_path)

            if not os.path.exists(file_directory):
                print(f"Created directory: {file_directory}")
                os.makedirs(file_directory)

            create_file(code_snippet, file_path)
        else:
            
            create_file(code_snippet, f"{project_directory}/.eng/{file_name}")
            print(
                f"{file_name} is not found in the project and placed in .eng folder"
            )


def create_file(code_snippet, file_path):
    """
    Creates a file with the given path and writes the provided code snippet to it.

    :param code_snippet: An object containing the code to be written into the file.
    :param file_path: The path where the file should be created. If the file already exists, it will be overwritten with the new content.
    :return: None. Outputs a message indicating the file creation status or an error message if an exception occurs.
    """
    try:
        with open(file_path, "w", newline="\n") as file:
            print(f"File created: {file_path}")
            file.write(code_snippet.code)
    except Exception as e:
        print("An error occurred:", e)


def join_paths(base_path, sub_path):
    """
    Joins two paths while avoiding duplication of common directory components,
    and creates the resulting directory if it doesn't exist.

    :param base_path: The base directory path.
    :param sub_path: The subdirectory or file path which might overlap with the base path.
    :return: The correctly joined path.
    """

    base_parts = os.path.normpath(base_path).split(os.sep)
    sub_parts = os.path.normpath(sub_path).split(os.sep)

    overlap_index = 0
    for sub_part in sub_parts:
        if sub_part in base_parts:
            overlap_index += 1
        else:
            break

    full_path = os.path.join(base_path, *sub_parts[overlap_index:])

    return full_path


def get_context_from_files(files):
    """
    Reads and returns the content from the given file paths.

    :param files: A string containing file paths.
    :return: Contents of the files as a single string.
    """
    file_paths = files.split("\n")

    file_contents = ""

    for path in file_paths:
        try:
            with open(f"workspace/{path}", "r") as file:
                content = file.read()
                file_contents += content + "\n"
        except FileNotFoundError:
            continue

    return file_contents
