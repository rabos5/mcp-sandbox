# mcp-sandbox
## setup instructions
This guide will help you set up and run the MCP server and client on your local machine using pyenv and poetry.

## Prerequisites
- [pyenv](https://github.com/pyenv/pyenv) for Python version management
- [poetry](https://python-poetry.org/) for dependency management
- [Ollama](https://ollama.ai/) installed and running locally

## Project Setup
### 1. Set up Python environment with pyenv
```bash
# Install Python 3.12.8 (or your preferred version)
pyenv install 3.12.8

# Set local Python version for the project
pyenv local 3.12.8
```

### 2. Initialize Poetry and install dependencies
```bash
poetry install --no-root
```

## Running the Application
### 1. Make sure Ollama is running with the llama3.2 model
```bash
# Pull the llama3.2 model if you haven't already
ollama pull llama3.2

# Verify Ollama is running
curl http://localhost:11434/api/version
```

### 2. Run the client stdio client example (from ./examples directory)
In a different terminal:
```bash
cd mcp-sandbox
poetry run python client_stdio.py
```

## Testing the Application
1. When the client starts, it will prompt you with "How can I help you today?"
2. Try asking addition-related questions like:
   - "What is the sum of 5 and 7?"
   - "Can you add 42.5 and 17.8?"
   - "Calculate 123 + 456"
3. Try asking non-math questions to see the direct LLM responses.

## Debugging
If you encounter any issues:
1. Check that Ollama is running and accessible at http://localhost:11434
2. Verify that the llama3.2 model is downloaded (`ollama list`)
3. Ensure the server and client are using the same tool names
4. Check the logs for any error messages

## Using the MCP Inspector (Alternative)
To use the visual MCP Inspector instead of the command-line client:

```bash
# Start the server
poetry run python server.py

# In another terminal, run the MCP Inspector
poetry run mcp dev server.py
```

## links:
- [anthropic news mcp](https://www.anthropic.com/news/model-context-protocol)
- [mcp docs](https://modelcontextprotocol.io/)
    - [for server developers](https://modelcontextprotocol.io/quickstart/server)
    - [for client developers](https://modelcontextprotocol.io/quickstart/client)
    - [for anthropic desktop](https://modelcontextprotocol.io/quickstart/user)
- [mcp - protocol / transport details]()
    - [stdio](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports#stdio)
    - [http with sse](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports#http-with-sse)
- [mcp python sdk - github](https://github.com/modelcontextprotocol/python-sdk)
- [mcp inspector - github](https://github.com/modelcontextprotocol/inspector)
- [json rpc message format specs](https://www.jsonrpc.org/specification)
- [simple diagram](https://excalidraw.com/#room=49425c43b5056c26b32a,gH9WmCt3kAgtECkg3vat7g)