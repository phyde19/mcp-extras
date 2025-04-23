# Model Context Protocol – Schema Cheatsheet (v2025‑03‑26)

## Hierarchy

```typescript
export type JSONRPCMessage =
  | JSONRPCRequest
  | JSONRPCNotification
  | JSONRPCResponse
  // error
  | JSONRPCError
  // batch
  | JSONRPCBatchRequest
  | JSONRPCBatchResponse;

export const LATEST_PROTOCOL_VERSION = "2025-03-26";
export const JSONRPC_VERSION = "2.0";

interface Request {};
interface Notification {};
interface Result {};



```

A one‑screen reference to the most important wire‑level types, constants, and method names defined in `schema/2025‑03‑26/schema.ts`.

---

## 🌐 Global Constants
| Symbol | Purpose |
| --- | --- |
| `LATEST_PROTOCOL_VERSION` | `"2025-03-26"` – tag used by clients/servers to assert compatibility |
| `JSONRPC_VERSION` | Always `"2.0"`; every envelope includes `jsonrpc:"2.0"` |

---

## 📨 Base JSON‑RPC Message Shapes
| Alias | Extends | Mandatory fields | Notes |
| --- | --- | --- | --- |
| **`JSONRPCRequest`** | `Request` | `jsonrpc`, `id`, `method`, optional `params` | Expects **response** |
| **`JSONRPCNotification`** | `Notification` | `jsonrpc`, `method`, optional `params` | **fire‑and‑forget**; no response |
| **`JSONRPCResponse`** | – | `jsonrpc`, `id`, `result` | Successful reply |
| **`JSONRPCError`** | – | `jsonrpc`, `id`, `error:{code,message,data?}` | Error reply |
| **Batch** | arrays | `JSONRPCBatchRequest`, `JSONRPCBatchResponse` | Parallel bundles |

Key helper types: `RequestId = string | number`, `ProgressToken`, `Cursor` (pagination).

---

## 🤝 Handshake Flow (Happy Path)
1. **`protocol/initialize`** → server replies with supported features & version.
2. **`protocol/registerServer`** (sent by server) advertises Resources, Tools, Prompts.
3. Client may call **`resources/list`**, **`prompts/list`**, etc.
4. Long‑lived session until **`protocol/shutdown`**.

---

## 📂 Resource API Methods
| Method | Purpose | Typical params/result |
| --- | --- | --- |
| `resources/list` | Paginate resource metadata | `{ cursor? }` → `{ resources:[…], nextCursor? }` |
| `resources/get` | Fetch full content of a single resource | `{ id }` → `{ resource }` |

Resource kinds (enum): `file`, `directory`, `webpage`, `database`, `custom`.
Common fields: `id`, `kind`, `uri`, `title`, `mtime`, `size`.

---

## 🛠️ Tool Invocation
| Method | Purpose |
| --- | --- |
| `tools/call` | Invoke a server‑exposed function. Params include `toolId`, `arguments`, optional `progressToken`. |

Tool descriptor: `{ id, name, description, parameters(JSON Schema), returns(JSON Schema) }`.

Progress streaming channel: notifications on `notifications/progress` keyed by the original request’s `progressToken`.

---

## 📝 Prompt API
| Method | Purpose |
| --- | --- |
| `prompts/list` | Enumerate pre‑built text templates |
| `prompts/get` | Retrieve a single prompt’s body/metadata |

Prompt object: `{ id, name, description, template, variables[] }`.

---

## 🔔 Standard Notifications
| Method | Payload | Emitted by |
| --- | --- | --- |
| `notifications/progress` | `{ progressToken, stage:<string>, pct?:number, message?:string }` | Any long‑running request |
| `notifications/serverLog` | `{ level:'info'|'warn'|'error', message }` | Server (optional) |

---

## ⚠️ Standard Error Codes
```
PARSE_ERROR      = -32700
INVALID_REQUEST  = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS   = -32602
INTERNAL_ERROR   = -32603
```
Servers may define custom `code >= -32099`.

---

## 🔑 Capability Flags (Example Sub‑set)
* `resources`: `true` if server implements Resource API.
* `tools`: `true` if Tool API available.
* `prompts`: `true` if Prompt API available.

Returned inside `protocol/registerServer` result.

---

### Quick Mental Model
> **MCP = JSON‑RPC 2.0 + three primitives (Resources 📂, Tools 🛠️, Prompts 📝) + handshake + progress streaming.**  Memorize the method names above and you can read any MCP trace.

---

*(Cheatsheet derived from schema/2025‑03‑26/schema.ts – 18 April 2025)*

