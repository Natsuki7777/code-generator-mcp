import os


def read_single_file_contents(file_path: str) -> str:
    """
    Read the contents of a single file.

    Args:
        file_path: Path to the file to read

    Returns:
        The contents of the file as text
    """
    # 絶対パスに変換
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."

    if not os.path.isfile(file_path):
        return f"Error: Path '{file_path}' is not a file."

    # Log information if context is available
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
    return content


if __name__ == "__main__":
    # Test the function
    test_file_path = "test.txt"  # Replace with your test file path
    print(read_single_file_contents(test_file_path))