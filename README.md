 # AI Agent Development Playground

 This repository contains scaffolding, notes, and example projects for building lean, composable AI agents without unnecessary abstractions.

 ## Context & Instructions for Future Self

 *Session Overview*:
 - Gathered guiding principles from leading AI teams (Anthropic, OpenAI, Windsurf, Cursor, Manus) focusing on:
   - Minimal glue layers (avoid heavy frameworks like LangChain)
   - Explicit orchestration in host language
   - First-class observability and telemetry
   - Composable, pure-function tools
   - Lean prompt engineering and cost controls
 - Added detailed guidelines in `codex-notes/agent_tooling_guidelines.md`.
 - Scaffolded an initial MCP (Model Context Protocol) "Hello World" project in `projects/hello-mcp/`:
   - `main.py`: FastAPI stub server with `/v1/models` and `/v1/chat/completions` returning a canned "Hello, world!" response.
   - `client.py`: httpx-based client that lists models and sends a "Say hello" chat request.
   - `README.md`: Setup and run instructions (using `fastapi dev main.py --reload --port 8000`).

 *Restoring Context After Restart*:
 1. Reopen this README to recall the high-level goals and structure.
 2. Review `codex-notes/agent_tooling_guidelines.md` for development principles.
 3. Navigate to `projects/hello-mcp/` and follow the setup steps to run the stub server and client demo.

 ## Next Steps
 - Expand MCP-based examples with more complex agent workflows.
 - Document testing strategies, orchestration patterns, and cost-monitoring templates in `codex-notes/`.
 - Iterate on new projects under `projects/` as we prototype additional use cases.


This was my original first message to you.
 Hey.. It's great to see you in this environment. This is a little meta but I want you to help me get dramatically better at building AI agents. Before we start can you teams behind products like windsurf, anthropic   │
│ claude, manus, chatgpt, cursor, etc. See what those teams have to say about tooling and modern effective non-bloat non-slop approaches to building AI software in 2025 and beyond. Note that most teams completely reject │
│  langchain and abstractions we don't need. I've also added this prompt in the readme file if you need to reference it again.   

I'm a strong programmer with decent experience building on top of native LLM apis from openai and anthropic. It's
currently 6:33 Pm Friday and I plan to spend the entire weekend deep diving into building agents with MCP and
dramatically improving my abilities to building software, tooling, etc on top of LLM apis. Please read the README.md in
the root of the project. This includes some initial research into how teams I respect are building agents (and the
bloated tools they're avoiding). This should guide our philosophy as we work. Once you read the readme please check
codex-notes which contains an mcp.md file documenting mcp and python-sdk.md which contains info about the python sdk
which will be our primary tool. Once you get acclimated I want us to plan some projects. In general the goal will be to
build progressively more demanding appications on top of existing MCP servers. We should start with a kind of hello
world project. Projects will go in the projects directory.

