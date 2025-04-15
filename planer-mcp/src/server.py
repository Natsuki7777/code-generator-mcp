from mcp.server.fastmcp import FastMCP
import os
from typing import Dict, List
import uvicorn

from read_file import read_single_file_contents
from ignore import load_gitignore
from tree import get_tree

PROJECT_NAME = os.environ.get("PROJECT_NAME", "Code Planer MCP Server")


# Initialize the MCP server
mcp = FastMCP(
    project_name="code-planer",
    instructions=f"Retrieve derectory structure and file contents for {PROJECT_NAME}"
)


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a single file.

    Args:
        file_path: Path to the file to read

    Returns:
        The contents of the file as text
    """
    return read_single_file_contents(file_path)


@mcp.tool()
def read_files(file_paths: List[str]) -> Dict[str, str]:
    """
    Read the contents of multiple files.

    Args:
        file_paths: List of paths to files to read

    Returns:
        A dictionary mapping file paths to their contents
    """
    result = {}
    for file_path in file_paths:
        result[file_path] = read_single_file_contents(file_path)
    return result


@mcp.tool()
def directory_structure(directory: str, max_depth: int = None, ignore_gitignore: bool = False) -> List[str]:
    """
    Get the directory structure as a list of strings.

    Args:
        directory: Path to the directory
        max_depth: Maximum depth of the directory tree
        ignore_gitignore: Whether to ignore .gitignore files
    Returns:
        A list of strings representing the directory structure
    """
    path = os.path.abspath(directory)
    if not os.path.exists(path):
        return f"Error: Directory '{path}' does not exist."

    gitignore_dict = None if not ignore_gitignore else load_gitignore(path)

    # ディレクトリ名と結果を文字列リストとして取得
    result = [f"📁 {os.path.basename(path)}"]

    # ツリーを生成
    tree = get_tree(path, "", gitignore_dict, max_depth=max_depth)
    result.extend(tree)

    return result


if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)
