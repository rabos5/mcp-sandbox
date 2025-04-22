import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from helper import *


async def main():
    # mcp server parameters - stdio
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        capture_stdout=True
    )
    
    # 1. open connection to mcp server locally
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 2. get available tools from mcp server
            mcp_tools_response = await session.list_tools()
            mcp_tools = mcp_tools_response.tools if hasattr(mcp_tools_response, "tools") else []

            # 3. convert tools from mcp server response to ollama api format
            ollama_tools = mcp_tools_2_ollama_tools(mcp_tools)

            # 4. get user prompt
            user_input = input("How can I help you today?\n")
            user_prompt = f"{user_input}"
            
            # 5. call ollama api
            print("calling ollama api...")
            ollama_response = await call_ollama_api(user_prompt, ollama_tools)
            ollama_response = ollama_response.get("response", "no response")
            
            print("ollama api response ->")
            print(ollama_response)
            
            # 6. parse tool calls from ollama api response
            tool_calls = await extract_tool_calls(ollama_response)
            
            if tool_calls:
                print(f"\ndetected {len(tool_calls)} tool call(s)")
                for tool_call in tool_calls:
                    name = tool_call["name"]
                    args = tool_call["arguments"]
                    print(f"Calling: {name} with {args}")
                    result = await session.call_tool(name, args)
                    print(f"result -> {result}")
            else:
                print("\nno tool calls detected... providing direct response ->")
                print(ollama_response)


if __name__ == "__main__":
    asyncio.run(main())