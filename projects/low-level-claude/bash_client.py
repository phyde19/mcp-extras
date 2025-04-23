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
            prompts: list[Any],
            history: list[dict[str, Any]], 
            system_message: str
        ):
        # clients
        self.anthropic = anthropic
        self.mcp_session = mcp_session
        # MCP Capabilities (protocol messages to retrieve)
        self.tools = tools
        self.prompts = prompts
        # Chat Context
        self.history = history
        self.system_message = system_message

    async def process_query(self, query: str) -> str:
        """process user query -> assistant message"""

        if query == '/run_prompt':
            # Run MCP server defined prompt
            prompt_name = self.prompts[0].name
            prompt_messages = (await self.mcp_session.get_prompt(prompt_name)).messages
            self.history.extend([
                {
                    "role": prompt.role,
                    "content": prompt.content.text
                }
                for prompt in prompt_messages
            ])
        
        else:
            # Run user defined prompt
            self.history.append({"role": "user", "content": query})

        # Evaluate any Tool Calls and Get assistant response
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

    system_message = (
        (await session.read_resource("text://system_prompt")).contents[0].text
    )

    # Get Tools
    response = await session.list_tools()
    tools = [{
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema
    } for tool in response.tools]

    # Get Resources
    resources = (await session.list_resources()).resources

    # Get Prompts
    prompts = (await session.list_prompts()).prompts

    chat = MCPAnthropicChat(
        anthropic=Anthropic(),
        mcp_session=session,
        tools=tools,
        prompts=prompts,
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
    args=["bash_server.py"],
    env=None
)

async def main():
    async with stdio_client(server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            # init
            await session.initialize()
            print("\nConnected to server")

            # ── tools ───────────────────────────────────────────────
            tools = (await session.list_tools()).tools
            print("Tools:", [tool.name for tool in tools])

            # ── resources ───────────────────────────────────────────
            resources = (await session.list_resources()).resources
            print("Resources:", [str(res.uri) for res in resources])

            # ── prompts ─────────────────────────────────────────────
            prompts = (await session.list_prompts()).prompts
            print("Available Prompts:", [prompt.name for prompt in prompts])
            
            # Run Chat
            await run_chat_loop(session)
            

if __name__ == "__main__":
    print("hello claude")
    print(f"starting subprocess mcp server '{server_params.args[0]}'")
    asyncio.run(main())