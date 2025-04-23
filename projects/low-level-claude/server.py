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
            uri="example://resource",  # type: ignore
            name="Example Resource"
        )
    ]

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    if str(uri) == "example://resource":
        return "This is a mocked example resource"
    raise ValueError("Resource not found")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="calculate_sum",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        ),
        types.Tool(
            name="get_weather",
            description="Returns the current weather for a given city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        )
    ]

def add(a: int, b: int) -> int:
    return a + b

def mock_get_weather(city: str) -> str:
    return f"The weather in {city} is sunny, 72°F."

ToolCallReturnValue = types.TextContent | types.ImageContent | types.EmbeddedResource

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[ToolCallReturnValue]:
    if name == "calculate_sum":
        result = add(arguments["a"], arguments["b"])
        return [types.TextContent(type="text", text=str(result))]

    if name == "get_weather":
        city = arguments["city"]
        result = mock_get_weather(city)
        return [types.TextContent(type="text", text=result)]

    raise ValueError(f"Tool not found: {name}")


# ────────────── Prompt definition ──────────────
PROMPT_TEXT = (
    "Please get the current temperature in New York City and Los Angeles using "
    "the get_weather tool. When you have both temperatures, add them together "
    "with the calculate_sum tool and report the total."
)

@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="sum_city_temps",
            description=(
                "Fetch the weather for NYC and LA, then add the two "
                "temperatures together."
            ),
            arguments_schema={},  # this prompt takes no arguments
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> types.GetPromptResult:
    if name != "sum_city_temps":
        raise ValueError(f"Prompt not found: {name}")

    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=PROMPT_TEXT),
            )
        ]
    )


async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
