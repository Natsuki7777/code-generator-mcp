import subprocess
from mcp.server.fastmcp import FastMCP
import os
from typing import Dict, List
import uvicorn

from read_file import read_single_file_contents
from tree_dir import get_tree_structure, load_base_gitignore
from search import search_codebase_function

PROJECT_NAME = os.environ.get("PROJECT_NAME", "Code Planer MCP Server")

# Initialize the MCP server
mcp = FastMCP(
    project_name="code-planer",
    instructions=f"Retrieve derectory structure and file contents for {PROJECT_NAME}"
)


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file

    Returns:
        The text contents of the requested file
    """
    content = read_single_file_contents(file_path)
    return content


@mcp.tool()
def directory_structure(directory: str, max_depth: int = None) -> str:
    """
    Get the directory structure as a list of strings.
    Args:
        directory: The directory path
        max_depth: The maximum depth to traverse
    Returns:
        A string representation of the directory structure
    """
    target_path = os.path.join("/", directory)
    base_path = os.path.join("/", PROJECT_NAME)
    # Load .gitignore files
    base_gitignore = load_base_gitignore(base_path, target_path)
    # Get the directory structure
    tree_structure = get_tree_structure(
        target_dir=target_path,
        current_depth=0,
        gitignore_parsers=base_gitignore,
        max_depth=max_depth
    )
    # Convert the list to a string
    tree_structure_str = "\n".join(tree_structure)
    return tree_structure_str


@mcp.tool()
def search_codebase(query: str, file_patterns: List[str] = None, case_sensitive: bool = False) -> List[Dict]:
    """
    Search for patterns across the codebase.

    Args:
        query: Search term or regex pattern
        file_patterns: File types to search (defaults to all)
        case_sensitive: Whether search should be case-sensitive

    Returns:
        List of matches with file location and context
    """
    code_root = os.path.join("/", PROJECT_NAME)
    matches = search_codebase_function(
        query=query,
        file_patterns=file_patterns,
        case_sensitive=case_sensitive,
        code_root=code_root
    )
    return matches


@mcp.tool()
def shell_command(command: str) -> str:
    """
    Execute a shell command.

    Args:
        command: The command to execute

    Returns:
        The output of the command

    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.stdout


@mcp.tool()
def code_base_info() -> str:
    """
    Get information about the code base.
    Contained information:
        - Project name
        - root directory path
        - Git status
        - directory structure (full structure)
        - Readme files in every directory

    Returns:
        Information about the server
    """
    return "Under construction"


if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)
