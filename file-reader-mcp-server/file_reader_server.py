from mcp.server.fastmcp import FastMCP, Context
import os
from typing import Dict, List
import sys
import uvicorn

PROJECT_NAME = os.environ.get("PROJECT_NAME", "file-reader-mcp-server")


# Initialize the MCP server
mcp = FastMCP(
    project_name="file-reader-mcp-server",
    instructions=f"File Reader MCP Server for {PROJECT_NAME}"
)


# File reader factory
@mcp.tool()
def read_file(file_path: str, ctx: Context = None) -> str:
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
    if ctx:
        ctx.info(f"Reading file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
    return content


@mcp.tool()
def read_files(file_paths: List[str], ctx: Context = None) -> Dict[str, str]:
    """
    Read the contents of multiple files.

    Args:
        file_paths: List of paths to files to read

    Returns:
        A dictionary mapping file paths to their contents
    """
    result = {}

    for file_path in file_paths:
        # Log information if context is available
        file_path = os.path.abspath(file_path)
        if ctx:
            ctx.info(f"Reading file: {file_path}")
        # Validate path
        if not os.path.exists(file_path):
            result[file_path] = f"Error: File '{file_path}' does not exist."
            continue

        if not os.path.isfile(file_path):
            result[file_path] = f"Error: Path '{file_path}' is not a file."
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            result[file_path] = content
        except Exception as e:
            result[file_path] = f"Error reading file: {str(e)}"

    return result


if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)
