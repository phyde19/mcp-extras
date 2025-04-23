from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
import asyncio

# Talk Name: mcp is good actually

from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env

class MCPAnthropicChat:
    def __init__(
            self, 
            anthropic: Anthropic, 
            mcp_session: ClientSession,
            tools: list[dict[str, Any]], 
            history: list[dict[str, Any]], 
            system_message: str
        ):
        self.anthropic = anthropic
        self.mcp_session = mcp_session
        self.tools = tools
        self.history = history
        self.system_message = system_message

    async def process_query(self, query: str) -> str:
        """process user query -> assistant message"""

        self.history.append({"role": "user", "content": query})

        while True:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=self.history,
                tools=self.tools,
                system=self.system_message
            )

            self.history.append({
                "role": "assistant",
                "content": response.content
            })

            tool_blocks = [
                content_block for content_block in response.content
                if content_block.type == "tool_use"
            ]

            # Break loop when Assistant is done calling tools
            if not tool_blocks:
                assistant_response = "\n".join(
                    content.text for content in response.content
                )
                return assistant_response
            
            # Handle Tool calls

            tool_results = []
            # get tool result for each tool call
            for tool_block in tool_blocks:
                name = tool_block.name
                args = tool_block.input 
                print(f"[Calling tool {name} with args {args}]")
                result = await self.mcp_session.call_tool(name, args)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result.content  # ant api accepts a str | list <- some serialization magic here
                })
            
            # append user tool message (yes user - Ant doesn't have Tool Messages)
            self.history.append({
                "role": "user",
                "content": tool_results
            })



async def run_chat_loop(session: ClientSession):
    """Run an interactive chat loop"""

    system_message = "You are a helpful assistant."

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
        mcp_session=session,
        tools=tools,
        history=[],
        system_message=system_message
    )

    print("\nMCP Anthropic Chat Started!")
    print("Type your queries or 'exit' to exit.")

    while True:
        try:
            # get user message
            query = input("\n>>: ").strip()

            if query.lower() == 'exit':
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

            # List available Resources
            response = await session.list_tools()
            tools = response.tools
            print("\nConnected to server with tools:", [tool.name for tool in tools])
            
            # Run Chat
            await run_chat_loop(session)
            

if __name__ == "__main__":
    print("hello claude")
    print(f"starting subprocess mcp server '{server_params.args[0]}'")
    asyncio.run(main())