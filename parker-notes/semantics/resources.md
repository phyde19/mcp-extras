# Resources

> ℹ️ **Info**  
> Resources are application/client controlled, and not generally model controlled. This means that different MCP clients decide how and when resources should be used within the implementation. 
> For example:
> - Claude Desktop currently requires users to explicitly select resources before they can be used
> - Other clients might automatically select resources based on heuristics
> - Some implementations may even allow the AI model itself to determine which resources to use 

Note that in order to expose data to models automatically, server authors should use a model-controlled primitive such as `Tools`.

---

## Overview - What are Resources?

#### Resource URIs

Resources are identified using URIs that follow this format:
```
[protocol]://[host]/[path]
```

For example:

- **`file:///home/user/documents/report.pdf`**
- **`postgres://database/customers/schema`**
- **`screen://localhost/display1`**


## Two kinds of Resources  

### **Text resources**

Text resources contain UTF-8 encoded text data. These are suitable for:

- Source code
- Configuration files
- Log files
- JSON/XML data
- Plain text

### **Binary resources**

Binary resources contain raw binary data encoded in base64. These are suitable for:

- Images
- PDFs
- Audio files
- Video files
- Other non-text formats

## Resource Discovery

Servers expose resources for client discovery using two primary methods

#### 1. Direct Resources
Servers expose a list of concrete resources via the resources/list endpoint. Each resource includes:
```typescript
{
  uri: string;           // Unique identifier for the resource
  name: string;          // Human-readable name
  description?: string;  // Optional description
  mimeType?: string;     // Optional MIME type
}
```

#### 2. Resource Templates 
For dynamic resources, servers can expose URI templates that clients can use to construct valid resource URIs:

```typescript
{
  uriTemplate: string;   // URI template following RFC 6570
  name: string;          // Human-readable name for this type
  description?: string;  // Optional description
  mimeType?: string;     // Optional MIME type for all matching resources
}
```
>TODO understand RFC 6570

## Reading Resources 
To read a resource, clients make a `resources/read` request with the resource URI.

The server responds with a list of resource contents:

```typescript
{
  contents: [
    {
      uri: string;        // The URI of the resource
      mimeType?: string;  // Optional MIME type

      // One of:
      text?: string;      // For text resources
      blob?: string;      // For binary resources (base64 encoded)
    }
  ]
}
```

The truth is that you could always do this. It's just about realizing how easy it is. you're always performing. This shit is what you were born to do you fucking bitch. Let's Fucking GOOOOO.


> ℹ️ **Info**  
> Servers may return multiple resources in response to one resources/read request. This could be used, for example, to return a list of files inside a directory when the directory is read.

## Resource Updates

Think about it. Resources can be updated in two ways
1. The set of available resources can change
2. The content of the resources can change

In the former, the server simply sends a notification to the client that the set/list of available resources has changed

In the latter, the client must first subscribe to updates pertaining to a resource. Then the the server can send notifications when a resource is updated.

Specifically:
1. Client sends **`resources/subscribe`** with resource URI
2. Server sends **`notifications/resources/updated`** when the resource changes
3. Client can fetch latest content with **`resources/read`**
4. Client can unsubscribe with **`resources/unsubscribe`**

## Python example implementation

```python
# Using the primitive server

app = Server("example-server")

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="file:///logs/app.log",
            name="Application Logs",
            mimeType="text/plain"
        )
    ]

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    if str(uri) == "file:///logs/app.log":
        log_contents = await read_log_file()
        return log_contents

    raise ValueError("Resource not found")

# Start server
async with stdio_server() as streams:
    await app.run(
        streams[0],
        streams[1],
        app.create_initialization_options()
    )
```







