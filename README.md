# MCP REST Server

A REST API wrapper for MCP-style tools, designed for integration with internal LLM gateways that don't support native MCP transport (like Claude Code CLI).

## Overview

This server provides a simple REST interface for LLM tool calling, returning tools in **Ollama format**:

- `GET /tools` - List all available tools (Ollama format)
- `POST /tools/call` - Execute a tool by name
- `GET /tools/{name}` - Get info about a specific tool
- `GET /health` - Health check

## Installation

```bash
# Install dependencies
poetry install

# Run the server
poetry run mcp-rest-server

# Or run directly with uvicorn
poetry run uvicorn mcp_rest_server.main:app --host 0.0.0.0 --port 8000 --reload
```

## Integration with fox-ui

Here's how to integrate this with your fox-ui backend:

### 1. Fetch Available Tools

When initializing or before making an LLM call, fetch the available tools:

```python
import requests

def get_mcp_tools(mcp_server_url="http://localhost:8000"):
    """Fetch available tools from the MCP REST server (Ollama format)."""
    response = requests.get(f"{mcp_server_url}/tools")
    response.raise_for_status()
    return response.json()["tools"]
```

### 2. Include Tools in LLM Request

Pass the tools directly to your Ollama-compatible API:

```python
async def chat_with_tools(user_message, mcp_server_url="http://localhost:8000"):
    # Get available tools (already in Ollama format)
    tools = get_mcp_tools(mcp_server_url)
    
    # Make request to your LLM gateway with tools
    llm_response = await call_llm_gateway(
        messages=[{"role": "user", "content": user_message}],
        tools=tools  # Pass directly - already in correct format
    )
    
    return llm_response
```

### 3. Handle Tool Use Responses

When the LLM wants to use a tool, execute it via the MCP server:

```python
import requests

def execute_mcp_tool(tool_name, arguments, mcp_server_url="http://localhost:8000"):
    """Execute a tool via the MCP REST server."""
    response = requests.post(
        f"{mcp_server_url}/tools/call",
        json={"name": tool_name, "arguments": arguments}
    )
    return response.json()
```

### 4. Complete Flow Example

```python
import requests
import json

MCP_SERVER = "http://localhost:8000"

async def handle_chat(user_message):
    # 1. Get tools (Ollama format)
    tools = get_mcp_tools(MCP_SERVER)
    
    # 2. Call LLM with tools
    response = await call_llm_gateway(
        messages=[{"role": "user", "content": user_message}],
        tools=tools
    )
    
    # 3. Check if LLM wants to use a tool
    # Ollama returns tool_calls in the message
    if response.get("message", {}).get("tool_calls"):
        tool_call = response["message"]["tool_calls"][0]
        
        # 4. Execute the tool
        tool_result = execute_mcp_tool(
            tool_name=tool_call["function"]["name"],
            arguments=tool_call["function"]["arguments"]
        )
        
        # 5. Send tool result back to LLM
        final_response = await call_llm_gateway(
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "", "tool_calls": [tool_call]},
                {"role": "tool", "content": json.dumps(tool_result["result"])}
            ],
            tools=tools
        )
        
        return final_response
    
    return response
```

## Available Tools

### get_daisyui_docs

Get DaisyUI v5 + Tailwind CSS v4 documentation for generating accurate UI code.

**Arguments:**
- `section` (string, optional): Name of a specific component/section to retrieve (e.g., "button", "modal", "colors")
- `list_components` (boolean, optional): If true, returns list of available components

**Examples:**

```bash
# Get full documentation
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_daisyui_docs", "arguments": {}}'

# List available components
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_daisyui_docs", "arguments": {"list_components": true}}'

# Get specific component docs
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_daisyui_docs", "arguments": {"section": "button"}}'
```

## Adding New Tools

1. Create a new file in `src/mcp_rest_server/tools/` (e.g., `my_tool.py`)
2. Implement your tool handler and registration function
3. Import and call the registration function in `tools/__init__.py`

Example:

```python
# src/mcp_rest_server/tools/my_tool.py

from .registry import register_tool

async def my_tool_handler(arguments: dict) -> dict:
    """Your tool logic here."""
    param = arguments.get("param", "default")
    return {"result": f"Processed: {param}"}

MY_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "param": {
            "type": "string",
            "description": "A parameter for the tool"
        }
    },
    "required": []
}

def register_my_tool():
    register_tool(
        name="my_tool",
        description="Description of what my tool does",
        input_schema=MY_TOOL_SCHEMA,
        handler=my_tool_handler
    )
```

Then in `tools/__init__.py`:

```python
from .my_tool import register_my_tool

def register_all_tools():
    register_daisyui_tool()
    register_my_tool()  # Add this line
```

## API Reference

### GET /tools

Returns all registered tools in Ollama format.

**Response:**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_daisyui_docs",
        "description": "Get DaisyUI v5 + Tailwind CSS v4 documentation...",
        "parameters": {
          "type": "object",
          "properties": {...},
          "required": []
        }
      }
    }
  ]
}
```

### GET /tools/{name}

Returns a specific tool in Ollama format.

**Response:**
```json
{
  "type": "function",
  "function": {
    "name": "get_daisyui_docs",
    "description": "...",
    "parameters": {...}
  }
}
```

### POST /tools/call

Execute a tool.

**Request:**
```json
{
  "name": "tool_name",
  "arguments": {}
}
```

**Response (success):**
```json
{
  "success": true,
  "result": {...}
}
```

**Response (error):**
```json
{
  "success": false,
  "error": "Error message"
}
```

## License

MIT
