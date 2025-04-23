import asyncio
import json
import subprocess
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from pydantic import AnyUrl

CONTAINER = "shared-box"
SANDBOX_DIR = "/home/sandbox"

# ─────────────────────────────────────────────
# Server initialization
# ─────────────────────────────────────────────

app = Server("bash-operator-server")

# ─────────────────────────────────────────────
# Resources
# ─────────────────────────────────────────────

SYSTEM_PROMPT_TEXT = """
You are a container‐shell operator agent.  
You can only run commands by calling the tool `run_in_container(command, workdir)`; you cannot run anything else.  
Each invocation is stateless—no directory, environment variable, or shell history is preserved between calls.  
Therefore, before every command you must specify the directory you want to work in.  
The tool will execute your command by doing:

    docker exec shared-box bash -c "cd <workdir> && <command>"

and will return:
- stdout: the command’s standard output
- stderr: the command’s standard error
- exit_code: the numeric exit code

Use full shell syntax (redirection, pipes, &&/||, quoting) inside the `command` string.  
Do not attempt to run `cd` by itself. Instead, always pass:

    { "command": "ls", "workdir": "/some/path" }

to list files in `/some/path`.  
Avoid dangerous operations like `rm -rf /` or `kill -9 1`.  
Be precise, minimal, and always include both parameters.
""".strip()

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="text://system_prompt",  # type: ignore
            name="System Prompt"
        )
    ]

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    if str(uri) == "text://system_prompt":
        return SYSTEM_PROMPT_TEXT
    raise ValueError("Resource not found")

# ─────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="run_in_container",
            description="Execute a bash command inside the persistent Docker container.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "workdir": {"type": "string"},
                },
                "required": ["command", "workdir"]
            }
        )
    ]

def _run(command: str, workdir: str) -> str:
    result = subprocess.run(
        ["docker", "exec", CONTAINER, "bash", "-c", f"cd {workdir} && {command}"],
        capture_output=True,
        text=True,
    )
    return json.dumps({
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    })

ToolReturn = types.TextContent

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[ToolReturn]:
    if name != "run_in_container":
        raise ValueError("Tool not found")

    cmd = arguments["command"]
    workdir = arguments["workdir"]
    result_json = _run(cmd, workdir)
    return [types.TextContent(type="text", text=result_json)]

# ─────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────

TITANIC_PROMPT = (
    "Can you give me some summary statistics about titantic passengers?"
    "Hint: You might need to write some python and put on your data scientist hat ;)"
)

@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="titanic",
            description="Simple demo showing the potential of computer use",
            arguments_schema={},
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> types.GetPromptResult:
    if name != "titanic":
        raise ValueError(f"Prompt not found: {name}")

    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=TITANIC_PROMPT),
            )
        ]
    )

# ─────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────

async def main():
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
