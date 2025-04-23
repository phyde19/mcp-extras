import asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import AnyUrl

app = Server("example-server")

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="example://resource", # type: ignore
            name="Example Resource"
        )
    ]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="calculate_sum",
            description="Add two numbers to gether",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
    ]


def add(a: int, b: int):
    return a + b

ToolCallReturnValue = types.TextContent | types.ImageContent | types.EmbeddedResource

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[ToolCallReturnValue]:
    if name == "calculate_sum":
        # call add user defined "add" function
        result = add(arguments["a"], arguments["b"])
        return [types.TextContent(type="text", text=str(result))]
    raise ValueError(f"Tool not found: {name}")

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())