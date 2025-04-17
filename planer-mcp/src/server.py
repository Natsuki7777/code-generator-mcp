from mcp.server.fastmcp import FastMCP
import os
from typing import Dict, List
import uvicorn

from read_file import read_single_file_contents
from tree_dir import get_tree_structure, load_base_gitignore

PROJECT_NAME = os.environ.get("PROJECT_NAME", "Code Planer MCP Server")

# Initialize the MCP server
mcp = FastMCP(
    project_name="code-planer",
    instructions=f"Retrieve derectory structure and file contents for {PROJECT_NAME}"
)


# Add file contents as a resource with template
@mcp.resource("file://{path}")
def get_file_content(path: str) -> str:
    """Get the contents of a file"""
    content = read_single_file_contents(path)
    print(f"file://{path} -> {content}")
    return content


@mcp.resource(f"file://{PROJECT_NAME}/README.md")
def get_project_readme() -> str:
    """Get README of the project"""
    # 絶対パスに変換
    content = read_single_file_contents(f"{PROJECT_NAME}/README.md")
    print(f"file://{PROJECT_NAME}/README.md -> {content}")
    return content


@mcp.tool()
def directory_structure(directory: str, max_depth: int = None, ignore_gitignore: bool = False) -> str:
    """
    Get the directory structure as a list of strings.
    Args:
        directory: The directory path
        max_depth: The maximum depth to traverse
        ignore_gitignore: Whether to ignore .gitignore files
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


if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)
