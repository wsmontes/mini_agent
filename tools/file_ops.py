"""File system operations tools."""

from typing import Dict, Any
import os
from pathlib import Path
from tools.base import BaseTool


class FileReadTool(BaseTool):
    """Read contents of a text file."""
    
    name = "read_file"
    description = "Read and return the contents of a text file"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to read"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)"
                }
            },
            "required": ["filepath"]
        }
        
    def execute(self, filepath: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file contents."""
        try:
            path = Path(filepath).expanduser().resolve()
            
            if not path.exists():
                return {
                    "error": f"File not found: {filepath}",
                    "filepath": str(path)
                }
                
            if not path.is_file():
                return {
                    "error": f"Not a file: {filepath}",
                    "filepath": str(path)
                }
                
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
                
            return {
                "filepath": str(path),
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except PermissionError:
            return {
                "error": f"Permission denied: {filepath}",
                "filepath": filepath
            }
        except Exception as e:
            return {
                "error": f"Error reading file: {str(e)}",
                "filepath": filepath
            }


class FileWriteTool(BaseTool):
    """Write content to a text file."""
    
    name = "write_file"
    description = "Write or append content to a text file"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                },
                "mode": {
                    "type": "string",
                    "enum": ["write", "append"],
                    "description": "Write mode: 'write' (overwrite) or 'append' (default: write)"
                }
            },
            "required": ["filepath", "content"]
        }
        
    def execute(self, filepath: str, content: str, mode: str = "write") -> Dict[str, Any]:
        """Write content to file."""
        try:
            path = Path(filepath).expanduser().resolve()
            
            # Create parent directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            file_mode = 'a' if mode == "append" else 'w'
            
            with open(path, file_mode, encoding='utf-8') as f:
                f.write(content)
                
            return {
                "filepath": str(path),
                "mode": mode,
                "bytes_written": len(content),
                "success": True
            }
            
        except PermissionError:
            return {
                "error": f"Permission denied: {filepath}",
                "filepath": filepath,
                "success": False
            }
        except Exception as e:
            return {
                "error": f"Error writing file: {str(e)}",
                "filepath": filepath,
                "success": False
            }


class FileListTool(BaseTool):
    """List files in a directory."""
    
    name = "list_directory"
    description = "List files and directories in a specified path"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list (default: current directory)"
                },
                "pattern": {
                    "type": "string",
                    "description": "Optional glob pattern to filter files (e.g., '*.txt')"
                }
            },
            "required": []
        }
        
    def execute(self, path: str = ".", pattern: str = None) -> Dict[str, Any]:
        """List directory contents."""
        try:
            dir_path = Path(path).expanduser().resolve()
            
            if not dir_path.exists():
                return {
                    "error": f"Path not found: {path}",
                    "path": str(dir_path)
                }
                
            if not dir_path.is_dir():
                return {
                    "error": f"Not a directory: {path}",
                    "path": str(dir_path)
                }
                
            if pattern:
                items = list(dir_path.glob(pattern))
            else:
                items = list(dir_path.iterdir())
                
            files = []
            directories = []
            
            for item in sorted(items):
                info = {
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size if item.is_file() else None
                }
                
                if item.is_file():
                    files.append(info)
                elif item.is_dir():
                    directories.append(info)
                    
            return {
                "path": str(dir_path),
                "pattern": pattern,
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories)
            }
            
        except PermissionError:
            return {
                "error": f"Permission denied: {path}",
                "path": path
            }
        except Exception as e:
            return {
                "error": f"Error listing directory: {str(e)}",
                "path": path
            }
