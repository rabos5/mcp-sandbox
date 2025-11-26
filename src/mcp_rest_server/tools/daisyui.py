"""
DaisyUI documentation tool.
Provides access to DaisyUI v5 + Tailwind CSS v4 documentation for LLM code generation.
"""

import os
from pathlib import Path

from .registry import register_tool


# Path to the bundled docs file (relative to this module)
DOCS_PATH = Path(__file__).parent.parent / "data" / "daisyui_instructions.md"

# Cache for the docs content
_docs_cache: str | None = None


def _load_docs() -> str:
    """Load the DaisyUI docs from the bundled file."""
    global _docs_cache
    
    if _docs_cache is not None:
        return _docs_cache
    
    if not DOCS_PATH.exists():
        raise FileNotFoundError(
            f"DaisyUI docs not found at {DOCS_PATH}. "
            "Please ensure daisyui_instructions.md is in the data directory."
        )
    
    _docs_cache = DOCS_PATH.read_text(encoding="utf-8")
    return _docs_cache


def _extract_section(content: str, section_name: str) -> str | None:
    """
    Extract a specific section from the markdown content.
    Sections are identified by ## headers.
    
    Args:
        content: The full markdown content
        section_name: Name of the section to extract (case-insensitive)
        
    Returns:
        The section content or None if not found
    """
    lines = content.split("\n")
    section_start = None
    section_lines = []
    
    section_name_lower = section_name.lower().strip()
    
    for i, line in enumerate(lines):
        # Check for section header (## or ###)
        if line.startswith("## ") or line.startswith("### "):
            header_text = line.lstrip("#").strip().lower()
            
            if section_start is not None:
                # We found the next section, stop collecting
                break
            
            if section_name_lower in header_text:
                section_start = i
                section_lines.append(line)
        elif section_start is not None:
            section_lines.append(line)
    
    if section_lines:
        return "\n".join(section_lines).strip()
    return None


def _list_components(content: str) -> list[str]:
    """
    List all component names from the docs.
    Components are identified by ### headers under the components section.
    """
    components = []
    in_components_section = False
    
    for line in content.split("\n"):
        if line.startswith("## daisyUI 5 components"):
            in_components_section = True
            continue
        
        if in_components_section:
            if line.startswith("## ") and "components" not in line.lower():
                # Reached next major section
                break
            if line.startswith("### "):
                component_name = line.lstrip("#").strip()
                components.append(component_name)
    
    return components


async def get_daisyui_docs(arguments: dict) -> dict:
    """
    Get DaisyUI v5 documentation for LLM code generation.
    
    Args:
        arguments: Dict that may contain:
            - section: Optional section name to filter (e.g., "button", "modal", "colors")
            - list_components: If True, return list of available components instead of docs
            
    Returns:
        Dict with documentation content and metadata
    """
    section = arguments.get("section")
    list_only = arguments.get("list_components", False)
    
    content = _load_docs()
    
    if list_only:
        components = _list_components(content)
        return {
            "type": "component_list",
            "components": components,
            "count": len(components),
            "hint": "Use the 'section' parameter to get detailed docs for a specific component"
        }
    
    if section:
        section_content = _extract_section(content, section)
        if section_content:
            return {
                "type": "section",
                "section": section,
                "content": section_content
            }
        else:
            # Try to find similar sections
            components = _list_components(content)
            similar = [c for c in components if section.lower() in c.lower()]
            return {
                "type": "error",
                "error": f"Section '{section}' not found",
                "similar_sections": similar[:5],
                "hint": "Try one of the similar sections, or use list_components=true to see all"
            }
    
    # Return full docs
    return {
        "type": "full_documentation",
        "content": content,
        "hint": "This is the complete DaisyUI v5 documentation. Use 'section' parameter to get specific component docs."
    }


# Tool input schema (JSON Schema format)
DAISYUI_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "section": {
            "type": "string",
            "description": "Optional: Name of a specific section or component to retrieve (e.g., 'button', 'modal', 'colors', 'accordion'). If not provided, returns the full documentation."
        },
        "list_components": {
            "type": "boolean",
            "description": "If true, returns a list of all available components instead of documentation content. Useful for discovering what's available.",
            "default": False
        }
    },
    "required": []
}


def register_daisyui_tool():
    """Register the DaisyUI documentation tool."""
    register_tool(
        name="get_daisyui_docs",
        description=(
            "Get DaisyUI v5 + Tailwind CSS v4 documentation for generating accurate UI code. "
            "DaisyUI provides CSS class names for common UI components. Use this tool when building "
            "web interfaces with DaisyUI to get the correct class names, component structures, and usage patterns. "
            "You can request the full documentation, a specific component/section, or list all available components."
        ),
        input_schema=DAISYUI_TOOL_SCHEMA,
        handler=get_daisyui_docs,
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
