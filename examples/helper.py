import aiohttp
import json
import re


OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


def get_system_prompt(tools = None):
    if not tools:
        return "You are a helpful assistant."

    system_message = "You are a helpful assistant with access to tools.\n\n"
    system_message += "Available tools:\n\n"
    
    for tool in tools:
        name = tool.get("name", "")
        description = tool.get("description", "")
        system_message += f"• {name}: {description}\n"

        example_args = {}
        if "parameters" in tool and "properties" in tool["parameters"]:
            for param_name, param_info in tool["parameters"]["properties"].items():
                if param_info.get("type") == "number":
                    example_args[param_name] = 5
                else:
                    example_args[param_name] = f"example_{param_name}"
        
        example_call = {
            "name": name,
            "arguments": example_args
        }

        system_message += f"Format tool call for {name} exactly as: {json.dumps(example_call)}\n\n"

    system_message += "Important instructions:\n"
    system_message += "1. Prioritize using tools when available.\n"
    system_message += "2. For general knowledge questions, respond directly without using tools.\n"
    system_message += "3. Format your tool calls exactly as shown in the examples above.\n"
    
    return system_message


async def call_ollama_api(prompt, tools):
    system_prompt = get_system_prompt(tools)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "tools": tools
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_API_URL, json=payload) as response:
            return await response.json()


async def extract_tool_calls(response):
    # todo: evaluate if truly necessary
    tool_call_matches = re.findall(r'{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*({[^}]+})\s*}', response)
    
    tool_calls = []
    for name, args_str in tool_call_matches:
        try:
            arguments = json.loads(args_str)
            tool_calls.append({"name": name, "arguments": arguments})
        except:
            print(f"could not parse arguments -> {args_str}")
    
    return tool_calls


def mcp_tools_2_ollama_tools(mcp_tools: list = []):
    ollama_tools = []
    for tool in mcp_tools:
        if not hasattr(tool, "name"):
            continue
            
        tool_name = tool.name
        print(f"found tool -> {tool_name}")
        
        ollama_tool = {
            "name": tool_name,
            "description": getattr(tool, "description", ""),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

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

    return ollama_tools