# Making sense of the low level Claude MCP Client 

## Transports
https://modelcontextprotocol.io/docs/concepts/transports#python-server

## Connecting to the server

**StdioServerParameters**
Server Parameters define the command parameters
needed to start the MCP stdio server
```
class StdioServerParameters(BaseModel):
    command: str
    args: list[str] = []
    env: dict[str, str] | None = None
```

**Initializing the session**
```
"""
Roughly Equivalent to:

params = StdioServerParameters(
    command="./server",
    args=["--option", "value"]
)

async with stdio_client(params) as (stdio, write):
    async with ClientSession(stdio, write) as session:
        ...
"""

exit_stack = AsyncExitStack()

stdio, write = exit_stack \
    .enter_async_context(stdio_client(server_params))

session: ClientSession = exit_stack \
    .enter_async_context(ClientSession(stdio, write))
```

**MCP Protocol Messages**
```
# Initialize the connection
await session.initialize()

# List available prompts
prompts = await session.list_prompts()

# Get a prompt
prompt = await session.get_prompt(
    "example-prompt", arguments={"arg1": "value"}
)

# List available resources
resources = await session.list_resources()

# List available tools
tools = await session.list_tools()

# Read a resource
content, mime_type = await session.read_resource("file://some/path")

# Call a tool
result = await session.call_tool("tool-name", arguments={"arg1": "value"})
```

**server imports & types**
```python
import mcp.types as types #types.Tool
```