"""
MCP REST Server tools package.
Import and register tools here.
"""

from .registry import register_tool, get_all_tools, get_tool, get_tool_ollama_format, execute_tool
from .daisyui import register_daisyui_tool


def register_all_tools():
    """Register all available tools."""
    register_daisyui_tool()
    # Add more tool registrations here as needed


__all__ = [
    "register_tool",
    "get_all_tools", 
    "get_tool",
    "get_tool_ollama_format",
    "execute_tool",
    "register_all_tools"
]
