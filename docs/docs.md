# Understanding MCP (Model Context Protocol): Context Engineering for LLM Agents
## What is MCP?
- Open protocol that standardizes how applications provide context for LLMs
- Enables connection between AI models and external data/tools
- Separates context provision from LLM interaction
- Think of it like a USB-C port for AI applications
- Developed by Anthropic, now open-sourced

## Scale Problem Solved (m + n vs. m * n) / Reusability
- Traditional approach: m clients × n data sources = m×n custom integrations
- MCP approach: m clients + n MCP servers = m+n connections
- Developers build against a standard protocol instead of custom connectors
- One MCP server can be used by multiple clients
- One MCP client can connect to multiple servers
- Eliminates duplication of integration efforts

## Examples:
### Addition Demo
- Server:
  - Exposes "add_numbers" tool via MCP protocol
  - Handles tool calls and returns results
- Client:
  - Connects to MCP server
  - Passes user prompt to LLM
  - Lets LLM decide when to call server tools
  - Returns results to user

#### Difference between .tool, .resource, and .prompt
- **Tools**: Function calls that perform actions (like POST endpoints)
  - Called by LLM when needed for a task
  - i.e. add numbers, search database, send email

- **Resources**: Data sources that provide context (like GET endpoints)
  - Provide data that is loaded into context when needed
  - i.e. file contents, configuration, user profiles

- **Prompts**: Templates for LLM interactions
  - Reusable patterns for specific tasks & can include context and instructions
  - i.e. code review template, debugging guide

### RAG Use Case


### What would this look like with AWS Bedrock?
- Replace Ollama with AWS Bedrock API (models need to support some level of tools understanding)
- Maintain same MCP server implementation
- Update client to use Bedrock API for LLM calls
- Create Bedrock-compatible tool call extraction
- Handle authentication with AWS credentials

## Constraints / Cons:
### Prompt Influence on Tool Usage
- Model needs clear instructions to use tools effectively
    - Can get complicated with layers of translation or system prompts
- Different models have varying abilities to handle tools
- Prompt engineering still required for optimal performance
- May need to adjust prompts based on model capabilities
- Context window limitations may affect what can be included

### Authentication
- Basic auth supported in protocol
- No standardized auth flow yet
- Each implementation handles security differently
- OAuth integration still emerging

### Local vs. Remote
- Local: Simple setup, no network concerns
- Remote: More complex, requires proper auth and security
- Tradeoffs between accessibility and security

### Possible performance issues
- Bulk processing (e.g., 50 acronyms via RAG) may encounter rate limiting
- Tools may execute sequentially by default
- Performance / resource concerns with large batches of operations

### Community / Evolving Changes:
- Requires community engagement / input for scalability / buy-in
- i.e. API / server developers to build / maintain MCP server tools / capabilities

## API / Protocol Details
- Based on JSON-RPC 2.0 message format
- Bi-directional communication
- Three core primitives: Tools, Resources, Prompts
- Two primary transport methods: stdio and HTTP with SSE

### JSON-RPC Message Format
- JSON-based protocol for remote procedure calls
- Message structure: method, params, id, jsonrpc
- Supports request-response pattern and notifications
- Simple, lightweight, language-agnostic

## Links:
- [Anthropic News MCP](https://www.anthropic.com/news/model-context-protocol)
- [MCP Documentation](https://modelcontextprotocol.io/)
  - [For Server Developers](https://modelcontextprotocol.io/quickstart/server)
  - [For Client Developers](https://modelcontextprotocol.io/quickstart/client)
  - [For Anthropic Desktop](https://modelcontextprotocol.io/quickstart/user)
- MCP Protocol/Transport Details
  - [stdio](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports#stdio)
  - [HTTP with SSE](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports#http-with-sse)
- [MCP Python SDK - GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector - GitHub](https://github.com/modelcontextprotocol/inspector)
- [JSON-RPC Message Format Specs](https://www.jsonrpc.org/specification)
- [Simple Diagram](https://excalidraw.com/#room=49425c43b5056c26b32a,gH9WmCt3kAgtECkg3vat7g)