from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Create the server
mcp = FastMCP("file-reader")

@mcp.tool()
async def read_file(file_path: str) -> str:
    """Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        Contents of the file as a string, or an error message
    """
    try:
        path = Path(file_path).expanduser().resolve()
        
        # Basic security check - this can be enhanced based on your needs
        if not os.path.exists(path):
            return f"Error: File not found: {file_path}"
        
        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return content
    except PermissionError:
        return f"Error: Permission denied for file: {file_path}"
    except IsADirectoryError:
        return f"Error: Path is a directory, not a file: {file_path}"
    except UnicodeDecodeError:
        return f"Error: File is not a text file or has an unsupported encoding: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get metadata information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file metadata (character count, creation time, modification time, etc.)
    """
    try:
        path = Path(file_path).expanduser().resolve()
        
        if not os.path.exists(path):
            return {"error": f"File not found: {file_path}"}
        
        # Get file stats
        stat_info = os.stat(path)
        
        # Format the info as a dictionary
        file_info = {
            "path": str(path),
            "exists": True,
            "size_bytes": stat_info.st_size,
            "size_human": format_size(stat_info.st_size),
            "is_file": os.path.isfile(path),
            "is_dir": os.path.isdir(path),
            "created_at": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "accessed_at": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            "permissions": oct(stat_info.st_mode)[-3:],  # Get the last 3 digits of octal representation
        }
        
        # Count characters if it's a text file
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_info["character_count"] = len(content)
            except UnicodeDecodeError:
                file_info["character_count"] = "Not a UTF-8 encoded text file"
            except Exception as e:
                file_info["character_count"] = f"Error counting characters: {str(e)}"
        
        return file_info
    except PermissionError:
        return {"error": f"Permission denied for file: {file_path}"}
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}

@mcp.tool()
async def batch_read_files(file_paths: List[str]) -> Dict[str, str]:
    """Read multiple files at once.
    
    Args:
        file_paths: List of paths to files to read
        
    Returns:
        Dictionary mapping file paths to their contents or error messages
    """
    results = {}
    
    for file_path in file_paths:
        try:
            path = Path(file_path).expanduser().resolve()
            
            if not os.path.exists(path):
                results[file_path] = f"Error: File not found"
                continue
                
            if not os.path.isfile(path):
                results[file_path] = f"Error: Path is not a file"
                continue
                
            # Read the file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            results[file_path] = content
        except PermissionError:
            results[file_path] = "Error: Permission denied"
        except UnicodeDecodeError:
            results[file_path] = "Error: File is not a text file or has unsupported encoding"
        except Exception as e:
            results[file_path] = f"Error: {str(e)}"
    
    return results

@mcp.tool()
async def batch_get_file_info(file_paths: List[str]) -> Dict[str, Dict[str, Any]]:
    """Get metadata for multiple files at once.
    
    Args:
        file_paths: List of paths to files
        
    Returns:
        Dictionary mapping file paths to their metadata
    """
    results = {}
    
    for file_path in file_paths:
        try:
            path = Path(file_path).expanduser().resolve()
            
            if not os.path.exists(path):
                results[file_path] = {"error": "File not found"}
                continue
            
            # Get file stats
            stat_info = os.stat(path)
            
            # Format the info as a dictionary
            file_info = {
                "path": str(path),
                "exists": True,
                "size_bytes": stat_info.st_size,
                "size_human": format_size(stat_info.st_size),
                "is_file": os.path.isfile(path),
                "is_dir": os.path.isdir(path),
                "created_at": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed_at": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                "permissions": oct(stat_info.st_mode)[-3:],
            }
            
            # Count characters if it's a text file
            if os.path.isfile(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_info["character_count"] = len(content)
                except UnicodeDecodeError:
                    file_info["character_count"] = "Not a UTF-8 encoded text file"
                except Exception as e:
                    file_info["character_count"] = f"Error counting characters: {str(e)}"
            
            results[file_path] = file_info
        except PermissionError:
            results[file_path] = {"error": "Permission denied"}
        except Exception as e:
            results[file_path] = {"error": f"{str(e)}"}
    
    return results

def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    # Define size units
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    # Convert to appropriate unit
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    # Format with one decimal place if not bytes
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"

# Run the server if this file is executed directly
if __name__ == "__main__":
    mcp.run()