#!/usr/bin/env python3
"""
File Operations MCP Server

This MCP server provides tools for file operations including:
- Reading files
- Writing/editing files
- Moving files
- Creating directories
- Removing files/directories

It's designed to be used by a Coder AI under instruction from a Planer AI.
"""

import os
import shutil
from pathlib import Path

from mcp.server.fastmcp import FastMCP 
import uvicorn
import subprocess

PROJECT_NAME = os.environ.get("PROJECT_NAME", "file-editor-mcp-server")

# Create an MCP server
mcp = FastMCP(
    project_name=PROJECT_NAME,
    instructions=f"File Editor MCP Server for {PROJECT_NAME}"
)


@mcp.resource("file://{path}")
def read_file(file_path: str) -> str:
    """
    Read the content of a file.

    Args:
        file_path: Path to the file

    Returns:
        The content of the file as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return f"[Binary file: {file_path}]"


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file, creating it if it doesn't exist.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Confirmation message

    Raises:
        PermissionError: If the file cannot be written due to permissions
    """
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return f"Successfully wrote to {file_path}"


@mcp.tool()
def replace_file_content(file_path: str, old_content: str, new_content: str) -> str:
    """
    Replace content in a file.

    Args:
        file_path: Path to the file
        old_content: Content to replace
        new_content: New content to write

    Returns:
        Confirmation message

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file cannot be written due to permissions
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace(old_content, new_content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return f"Successfully replaced content in {file_path}"


@mcp.tool()
def insert_file_content(file_path: str, content: str, line_number: int) -> str:
    """
    Insert content into a file at a specific line number.

    Args:
        file_path: Path to the file
        content: Content to insert
        line_number: Line number to insert the content 0-indexed

    Returns:
        Confirmation message

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file cannot be written due to permissions
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()


    lines.insert(line_number, content + '\n')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return f"Successfully inserted content into {file_path} at line {line_number}"

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
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.stdout



if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)
