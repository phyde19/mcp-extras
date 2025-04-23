# JSON‑RPC 2.0 Cheatsheet

A friendly, empathetic guide to the core JSON‑RPC 2.0 concepts you’ll need for MCP (and beyond). Think of this as your quick‑start companion, not a dry spec dump.

---

## 🔖 Version Declaration
Every message **must** start by declaring the protocol version—this lets both sides agree on the rules:
```json
{ "jsonrpc": "2.0" }
```
> *Tip:* If you see anything other than `"2.0"`, the server or client may not understand your message.

---

## 1️⃣ Request → Response
**What it does:** invoke a remote procedure, wait for the result.

```jsonc
// Client → Server: ask for sum
{ "jsonrpc": "2.0", "method": "sum", "params": [1,2], "id": 1 }

// Server → Client: returns result
{ "jsonrpc": "2.0", "result": 3, "id": 1 }
```
- **`id`** links the request to its response.
- **`params`** can be an array (positional) or object (named).
> *Why it matters:* Always include an `id` if you expect a reply—forgetting it turns your call into a silent notification.

---

## 2️⃣ Notification (No Reply)
**What it does:** send information without waiting for confirmation.

```json
{ "jsonrpc": "2.0", "method": "notify", "params": { "msg": "hello" } }
```
- **No `id` field** → no response will come.
> *Usage tip:* Great for fire‑and‑forget operations like logging or heartbeat signals. Be mindful: you won’t know if it fails.

---

## 3️⃣ Error Response
**What it does:** informs you when something goes wrong.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": null
  }
}
```
- **`code`** indicates the type of error; see codes below.
- **`message`** gives a brief human‑readable reason.
> *Friendly pointer:* Always check both `result` **and** `error`. An absent `error` implies success.

---

## 4️⃣ Batch Call
**What it does:** bundle multiple calls into one payload, improving efficiency.

```json
[
  { "jsonrpc": "2.0", "method": "add",      "params": [1,2],       "id": 1 },
  { "jsonrpc": "2.0", "method": "log",      "params": ["x"]             },
  { "jsonrpc": "2.0", "method": "subtract", "params": {"a":5,"b":3}, "id": 2 }
]
```
- Server responds with an array of Responses/Errors for entries that included an `id`.
> *Pro tip:* Keep each entry independent—one failing call won’t block the others.

---

## ⚠️ Standard Error Codes
Understand these common codes so you can diagnose issues quickly:
```text
-32700 PARSE_ERROR      // Malformed JSON, can’t parse
-32600 INVALID_REQUEST  // JSON doesn’t map to a valid Request
-32601 METHOD_NOT_FOUND // Called method doesn’t exist
-32602 INVALID_PARAMS   // Parameters don’t match the method signature
-32603 INTERNAL_ERROR   // Server-side exception or bug
```
Custom application errors live in **-32099..-32000**.
> *Quick advice:* Log the `code` and `message`—it’s your fastest path to root‑causing failures.

---

## 🌐 Transport Neutral
JSON‑RPC defines **only** the message format and semantics. You choose the transport:
- **HTTP/HTTPS** – common for web APIs
- **WebSocket** – real‑time, full‑duplex communication
- **stdin/stdout** – as used by LSP and MCP clients
- **Raw TCP** – lightweight, custom protocols

> *Remember:* No matter where you send it, the JSON envelope stays the same.

---

### 🎯 Minimal Example
A final “hello world” to cement the pattern:
```json
// Requesting multiplication
{ "jsonrpc": "2.0", "method": "multiply", "params": [3,4], "id": 7 }

// Successful response
{ "jsonrpc": "2.0", "result": 12, "id": 7 }
```
> *You’ve got this!* Keep these blocks in mind, and you’ll decode or construct any JSON‑RPC call like a pro.

