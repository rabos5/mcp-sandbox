"""
MCP REST Server - A REST API wrapper for MCP-style tools.

This server provides REST endpoints for LLM tool calling, designed for integration
with internal LLM gateways that don't support native MCP transport.

Endpoints:
    GET  /tools       - List all available tools (Ollama format)
    POST /tools/call  - Execute a tool by name
    GET  /health      - Health check
"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .tools import register_all_tools, get_all_tools, execute_tool, get_tool, get_tool_ollama_format


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - register tools on startup."""
    register_all_tools()
    yield


app = FastAPI(
    title="MCP REST Server",
    description="REST API wrapper for MCP-style tools, enabling LLM tool calling via HTTP",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-rest-server"}


@app.get("/tools")
async def list_tools():
    """
    List all available tools in Ollama tool format.
    
    Returns a list of tool definitions that can be passed directly to
    Ollama's /api/chat tools parameter.
    
    Response format:
    {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "tool_name",
                    "description": "What the tool does",
                    "parameters": { ... JSON Schema ... }
                }
            },
            ...
        ]
    }
    """
    tools = get_all_tools()
    return {"tools": tools}


@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """
    Get information about a specific tool in Ollama format.
    
    Args:
        tool_name: Name of the tool to look up
        
    Returns:
        Tool definition in Ollama format or 404 if not found
    """
    tool = get_tool_ollama_format(tool_name)
    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found"
        )
    
    return tool


@app.post("/tools/call")
async def call_tool(request: Request):
    """
    Execute a tool by name with the given arguments.
    
    This endpoint is designed to handle tool_use blocks from LLM responses.
    
    Request body:
    {
        "name": "tool_name",
        "arguments": { ... tool arguments ... }
    }
    
    Response (success):
    {
        "success": true,
        "result": { ... tool output ... }
    }
    
    Response (error):
    {
        "success": false,
        "error": "Error message"
    }
    """
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON in request body"
        )
    
    # Validate request structure
    if not isinstance(body, dict):
        raise HTTPException(
            status_code=400,
            detail="Request body must be a JSON object"
        )
    
    name = body.get("name")
    if not name:
        raise HTTPException(
            status_code=400,
            detail="Missing required field: 'name'"
        )
    
    if not isinstance(name, str):
        raise HTTPException(
            status_code=400,
            detail="Field 'name' must be a string"
        )
    
    arguments = body.get("arguments", {})
    if not isinstance(arguments, dict):
        raise HTTPException(
            status_code=400,
            detail="Field 'arguments' must be an object"
        )
    
    # Execute the tool
    result = await execute_tool(name, arguments)
    
    # Return appropriate status code based on success
    if result["success"]:
        return JSONResponse(content=result, status_code=200)
    else:
        # Tool not found or execution error
        return JSONResponse(content=result, status_code=400)


def run():
    """Entry point for running the server via poetry script."""
    import uvicorn
    uvicorn.run(
        "mcp_rest_server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    run()
