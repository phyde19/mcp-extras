# MCP Integration Quickstart

A concise guide for wiring MCP into your product today.

---

## 1. The 30‑Second Mental Model

| Classic RPC | MCP |
|-------------|-----|
| One request → one response → socket can die. | Session handshake (initialize) → long-lived stream → either side may send requests, results, notifications until transport closes. |
| Server never calls client. | Server issues own requests (e.g., sampling/createMessage, roots/list); client behaves as mini-server. |
| Progress via polling. | Built-in notifications/progress with cancellation. |
| Schema fixed at compile-time. | Capabilities negotiated at handshake (`ClientCapabilities`, `ServerCapabilities`). |
| Pure functions. | Tools, resources, prompts with payloads and side effects. |

---

## 2. End-to-End Message Flow

```sql
Client                Transport (WebSocket/SSE/stdio)              Server
┆ open stream ┆ ───────────────────────────────────────────────▶ ┆ open stream ┆
InitializeRequest ─────────────────────────────────────────────▶
                               InitializeResult ────────────────▶
notifications/initialized ─────────────────────────────────────▶
               tools/call ... etc.  ⇄   (progress / logs / pushes)
┆ close stream ┆ ◀────────────────────────────────────────────── ┆ close stream ┆
```

- All JSON framed as JSON-RPC 2.0.
- `id` correlates request/result.
- Method names match schema.

---

## 3. Minimal Runnable Example

### 3.1 Server (python-sdk)
```python
from mcp.fast import FastMCP

mcp = FastMCP("calc-server", version="1.0.0")

@mcp.tool(name="math/add")
def add(a: int, b: int) -> str:
    return str(a + b)

if __name__ == "__main__":
    mcp.run_stdio()  # use .run_sse(host, port) for SSE
```

**Under the Hood:**

| Code line        | Schema object generated                                     |
|------------------|-------------------------------------------------------------|
| `FastMCP(...)`   | `InitializeResult.serverInfo`, `ServerCapabilities`         |
| `@mcp.tool`      | Tool entry in `ListToolsResult`, callable via `CallToolRequest` |
| `mcp.run_stdio()` | Opens duplex stream, parses `JSONRPCMessage`, routes to tool |

### 3.2 Client
```python
from mcp.client import ClientSession

async with ClientSession.auto_connect("./calc-server") as session:
    result = await session.call_tool("math/add", a=4, b=3)
    print(result.content[0].text)  # "7"
```

**ClientSession Automatically:**
- Sends `InitializeRequest`.
- Waits for `InitializeResult`.
- Fires `notifications/initialized`.
- Serializes `CallToolRequest`, parses `CallToolResult`.
- Keeps stream open for progress/server pushes.

---

## 4. Features You'll Regret Skipping

| Feature                | Why You Need It                             | How to Toggle                     |
|------------------------|---------------------------------------------|-----------------------------------|
| Progress tokens        | Show completion %, allow cancellation       | Supply `params._meta.progressToken` |
| Server logging         | Real-time debugging                         | Client sends `logging/setLevel`   |
| Subscriptions          | Push updates on file/DB changes             | Use `resources/subscribe`, `unsubscribe` |
| Sampling back-channel  | Server delegates LLM calls to client        | Implement `handle_sampling_message` callback |
| Roots                  | Server access to project dirs               | Respond to `roots/list`           |

---

## 5. Gotchas & Fixes

| Symptom                                        | Cause                                     | Fix                                 |
|------------------------------------------------|-------------------------------------------|-------------------------------------|
| Server disconnects after first request         | Skipped Initialize steps                  | Use SDK helpers, never send `tools/call` first |
| "Method not found" errors                      | Tool name mismatch                        | Check `ListToolsResult` JSON        |
| No progress received                           | Missing `progressToken`                   | Add `_meta: {progressToken: "abc"}` |
| Batch calls unsupported                        | Python SDK v0.5 lacks batch request wrapper | Send raw JSON via `session.transport.send_raw` |

---

## 6. Roadmap: Next Steps

- Study `schema.ts`: Resources, Tools, Prompts payload shapes.
- Check `mcp/types.py`: Pydantic mirrors schema interfaces.
- Read SDK transport docs (stdio/SSE/WebSocket).
- Understand capability negotiation patterns.

---

## TL;DR

- MCP is a persistent conversation channel, not one-shot RPC.
- Workflow: Open stream → Handshake → Bidirectional messaging with rich schema.
- Leverage Python SDK abstractions (`FastMCP`, `ClientSession`) to simplify integration.

