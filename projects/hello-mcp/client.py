#!/usr/bin/env python3
"""
Minimal MCP client for the hello-world server.
Uses stdio transport to start and communicate with the server.
"""
import asyncio

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession


async def main():
    # Assumes server.py is in the same directory
    params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            # List resources
            resources = await session.list_resources()
            print("Resources:", resources)

            # Read greeting for 'World'
            greeting_text, _ = await session.read_resource("greeting://World")
            print("Greeting:", greeting_text)

            # List tools
            tools = await session.list_tools()
            print("Tools:", [tool.name for tool in tools])

            # Call add tool
            result = await session.call_tool("add", arguments={"a": 2, "b": 3})
            print("Add result:", result)

if __name__ == "__main__":
    asyncio.run(main())