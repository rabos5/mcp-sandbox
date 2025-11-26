# client_sse.py
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from helper import *


async def main():
    sse_url = "http://localhost:8000/mcp"
    print(f"Connecting to MCP server at {sse_url}...")
    
    async with sse_client(sse_url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print("Connection initialized successfully!")
            
            # Get tools
            tools_response = await session.list_tools()
            tools_list = tools_response.tools if hasattr(tools_response, "tools") else []
            
            # Format tools for Ollama
            ollama_tools = []
            for tool in tools_list:
                if not hasattr(tool, "name"):
                    continue
                    
                tool_name = tool.name
                print(f"Found tool: {tool_name}")
                
                # Create Ollama-compatible tool
                ollama_tool = {
                    "name": tool_name,
                    "description": getattr(tool, "description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
                
                # Add parameters from schema
                schema = getattr(tool, "inputSchema", {})
                if isinstance(schema, dict) and "properties" in schema:
                    for prop_name, prop_info in schema["properties"].items():
                        ollama_tool["parameters"]["properties"][prop_name] = {
                            "type": prop_info.get("type", "string"),
                            "description": prop_info.get("title", prop_name)
                        }
                
                if isinstance(schema, dict) and "required" in schema:
                    ollama_tool["parameters"]["required"] = schema["required"]
                
                ollama_tools.append(ollama_tool)
            
            # User loop for multiple calculations
            while True:
                # Get user input
                user_input = input("\nEnter a math problem (e.g., 'What is the sum of 3 and 4?') or 'quit' to exit: ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Exiting...")
                    break
                
                user_prompt = f"Use the add_numbers_tool tool to solve this: {user_input}"
                
                # Call Ollama
                print("\nCalling Ollama API...")
                ollama_response = await call_ollama_api(user_prompt, ollama_tools)
                
                # Show response
                print("\nOllama response:")
                print(ollama_response.get("response", "No response"))
                
                # Process tool calls
                tool_calls = await extract_tool_calls(ollama_response)
                
                if tool_calls:
                    print(f"\nDetected {len(tool_calls)} tool call(s)")
                    for tool_call in tool_calls:
                        name = tool_call["name"]
                        args = tool_call["arguments"]
                        print(f"Calling: {name} with {args}")
                        result = await session.call_tool(name, args)
                        print(f"Result: {result}")
                else:
                    print("\nNo tool calls found. Using fallback...")
                    # Fallback: extract numbers directly
                    numbers = re.findall(r"\d+\.?\d*", user_input)
                    if len(numbers) >= 2:
                        x, y = float(numbers[0]), float(numbers[1])
                        print(f"Extracted numbers: {x} and {y}")
                        result = await session.call_tool("add_numbers_tool", {"x": x, "y": y})
                        print(f"Result: {result}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")