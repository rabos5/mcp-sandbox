def convert_ollama_tools_to_bedrock(ollama_tools: list[dict]) -> list[dict]:
    bedrock_tools = []
    
    for tool in ollama_tools:
        func = tool.get("function", {})
        
        bedrock_tool = {
            "toolSpec": {
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "inputSchema": {
                    "json": func.get("parameters", {"type": "object", "properties": {}})
                }
            }
        }
        bedrock_tools.append(bedrock_tool)
    
    return bedrock_tools


def convert_bedrock_tools_to_ollama(bedrock_tools: list[dict]) -> list[dict]:
    ollama_tools = []
    
    for tool in bedrock_tools:
        spec = tool.get("toolSpec", {})
        
        ollama_tool = {
            "type": "function",
            "function": {
                "name": spec.get("name", ""),
                "description": spec.get("description", ""),
                "parameters": spec.get("inputSchema", {}).get("json", {"type": "object", "properties": {}})
            }
        }
        ollama_tools.append(ollama_tool)
    
    return ollama_tools


def convert_ollama_tools_to_openai(ollama_tools: list[dict]) -> list[dict]:
    openai_tools = []
    
    for tool in ollama_tools:
        func = tool.get("function", {})
        
        openai_tool = {
            "type": "function",
            "function": {
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "parameters": func.get("parameters", {"type": "object", "properties": {}})
            }
        }
        openai_tools.append(openai_tool)
    
    return openai_tools


def convert_openai_tools_to_ollama(openai_tools: list[dict]) -> list[dict]:
    ollama_tools = []
    
    for tool in openai_tools:
        func = tool.get("function", {})
        
        ollama_tool = {
            "type": "function",
            "function": {
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "parameters": func.get("parameters", {"type": "object", "properties": {}})
            }
        }
        ollama_tools.append(ollama_tool)
    
    return ollama_tools


# def convert_ollama_tools_to_openai(ollama_tools: list[dict]) -> list[dict]:
#     return [tool.copy() for tool in ollama_tools]


# def convert_openai_tools_to_ollama(openai_tools: list[dict]) -> list[dict]:
#     return [tool.copy() for tool in openai_tools]


import numpy as np


def chunk_docs(content: str) -> list[dict]:
    """Split docs into component-sized chunks."""
    chunks = []
    current_chunk = []
    current_header = "intro"
    
    for line in content.split("\n"):
        if line.startswith("### "):
            if current_chunk:
                chunks.append({
                    "header": current_header,
                    "content": "\n".join(current_chunk)
                })
            current_header = line.lstrip("#").strip()
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    if current_chunk:
        chunks.append({"header": current_header, "content": "\n".join(current_chunk)})
    
    return chunks


async def get_relevant_chunks(user_prompt: str, chunks: list[dict], embeddings: list, top_k: int = 5) -> str:
    """
    Get most relevant chunks using embedding similarity.
    Assumes you have pre-computed embeddings for each chunk.
    """
    # Get embedding for user prompt (using your gateway)
    prompt_embedding = await get_embedding(user_prompt)
    
    # Cosine similarity
    similarities = []
    for i, chunk_emb in enumerate(embeddings):
        sim = np.dot(prompt_embedding, chunk_emb) / (np.linalg.norm(prompt_embedding) * np.linalg.norm(chunk_emb))
        similarities.append((sim, i))
    
    # Get top-k
    similarities.sort(reverse=True)
    top_chunks = [chunks[i]["content"] for _, i in similarities[:top_k]]
    
    return "\n\n".join(top_chunks)