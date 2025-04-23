from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dataclasses import dataclass
import asyncio

class MCPAnthropicChat:
    def __init__(self, anthropic: Anthropic, tools: list[dict[str, Any]], history: list[dict[str, Any]]):
        self.anthropic = anthropic
        self.tools = tools
        self.history = history

    async def process_query(self, query: str) -> str:
        """process user query -> assistant message"""

        self.history.append({"role": "user", "content": query})

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=self.history,
            tools=self.tools
        )
        print(response)




async def run_chat_loop(session: ClientSession):
    """Run an interactive chat loop"""

    system_message = "You are a helpful assistant."
    history: list[dict[str, Any]] = [
        {"role": "system", "content": system_message}
    ]

    # Get Tools
    response = await session.list_tools()
    tools = [{
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema
    } for tool in response.tools]

    # Get Resources
    # TODO

    # Get Prompts
    # TODO

    chat = MCPAnthropicChat(
        anthropic=Anthropic(),
        tools=tools,
        history=history
    )

    print("\nMCP Anthropic Chat Started!")
    print("Type your queries or 'quit' to exit.")

    while True:
        try:
            # get user message
            query = input("\n>>: ").strip()

            if query.lower() == 'quit':
                break

            # process user message 
            response = await chat.process_query(query)
            print("\n" + response)

        except Exception as e:
            print(f"\nError: {str(e)}")


server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env=None
)

async def main():
    async with stdio_client(server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            # init
            await session.initialize()

            # List available tools
            response = await session.list_tools()
            tools = response.tools
            print("\nConnected to server with tools:", [tool.name for tool in tools])
            
            # Run Chat
            await run_chat_loop(session)
            

if __name__ == "__main__":
    print("hello claude")
    print(f"starting subprocess mcp server '{server_params.args[0]}'")
    asyncio.run(main())