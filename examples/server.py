from mcp.server.fastmcp import FastMCP
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_sandbox_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_sandbox_server")


mcp = FastMCP("mcp sandbox - server")
logger.info("mcp sandbox server initialized")

# math
@mcp.tool()
def add_numbers_tool(x: float, y: float) -> str:
    logger.info(f"add_numbers_tool called with parameters x={x}, y={y}")
    result = x + y
    logger.info(f"add_numbers_tool result -> {result}")

    return f"Adding {x} and {y} yields {result}"


@mcp.tool()
def subtract_numbers_tool(x: float, y: float) -> str:
    logger.info(f"subtract_numbers_tool called with parameters x={x}, y={y}")
    result = x - y
    logger.info(f"subtract_numbers_tool result -> {result}")

    return f"Subtracting {x} from {y} yields {result}"


# @mcp.prompt()
# def add_numbers_prompt() -> str:
#     return """You are an assistant that helps with addition.
#     When asked to add numbers or perform addition, you should:
#     1. Identify the two numbers in the user's query
#     2. Use the add_numbers tool to calculate their sum
#     3. Return the result to the user
    
#     Example:
#     User: What is the sum of 42.5 and 17.8?
#     You: [Use the add_numbers tool with x=42.5, y=17.8]
#     """


# rag - get acronym definition from API
# @mcp.tool()
# def get_acronym_definition(acronym: str):
#     # todo implement the requests api call to get the definition for given acronym
#     definition = "placeholder definition"
#     return f"{acronym} - {definition}"


# # echo samples
# @mcp.resource("echo://{message}")
# def echo_resource(message: str) -> str:
#     return f"sample - resource echo: {message}"


# @mcp.tool()
# def echo_tool(message: str) -> str:
#     return f"sample - tool echo: {message}"


# @mcp.prompt()
# def echo_prompt(message: str) -> str:
#     return f"sample - process this message: {message}"


if __name__ == "__main__":
    mcp.run()