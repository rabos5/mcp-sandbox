"""
Tool registry for managing MCP-style tools.
Provides registration, listing, and execution of tools.
"""

from typing import Callable, Any

# Global tool registry
_tools: dict[str, dict] = {}


def register_tool(
    name: str,
    description: str,
    input_schema: dict,
    handler: Callable,
    annotations: dict | None = None
) -> None:
    """
    Register a tool with the registry.
    
    Args:
        name: Unique tool name (e.g., "get_daisyui_docs")
        description: Human-readable description of what the tool does
        input_schema: JSON Schema describing the tool's input parameters
        handler: Async function that executes the tool
        annotations: Optional MCP annotations (readOnlyHint, etc.)
    """
    _tools[name] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "handler": handler,
        "annotations": annotations or {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    }


def get_all_tools() -> list[dict]:
    """
    Get all registered tools in Ollama tool format.
    
    Returns:
        List of tool definitions suitable for Ollama API tool calling.
        Format: {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}
    """
    tools = []
    for tool_data in _tools.values():
        tools.append({
            "type": "function",
            "function": {
                "name": tool_data["name"],
                "description": tool_data["description"],
                "parameters": tool_data["input_schema"]
            }
        })
    return tools


def get_tool(name: str) -> dict | None:
    """
    Get a specific tool by name.
    
    Args:
        name: The tool name to look up
        
    Returns:
        Tool data dict (internal format) or None if not found
    """
    return _tools.get(name)


def get_tool_ollama_format(name: str) -> dict | None:
    """
    Get a specific tool by name in Ollama format.
    
    Args:
        name: The tool name to look up
        
    Returns:
        Tool definition in Ollama format or None if not found
    """
    tool_data = _tools.get(name)
    if not tool_data:
        return None
    
    return {
        "type": "function",
        "function": {
            "name": tool_data["name"],
            "description": tool_data["description"],
            "parameters": tool_data["input_schema"]
        }
    }


async def execute_tool(name: str, arguments: dict | None = None) -> dict:
    """
    Execute a tool by name with the given arguments.
    
    Args:
        name: The tool name to execute
        arguments: Dict of arguments to pass to the tool handler
        
    Returns:
        Dict with 'success' bool and either 'result' or 'error'
    """
    tool = _tools.get(name)
    if not tool:
        return {
            "success": False,
            "error": f"Tool '{name}' not found. Available tools: {list(_tools.keys())}"
        }
    
    try:
        handler = tool["handler"]
        result = await handler(arguments or {})
        return {
            "success": True,
            "result": result
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid arguments: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution failed: {type(e).__name__}: {str(e)}"
        }
