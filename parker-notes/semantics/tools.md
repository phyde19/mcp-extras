# Tools

> ℹ️ **Info**  
> Tools are designed to be model-controlled. 
> This means tools are designed for model function/tool calling as the primay interface.


## Overview 

Tools are distinct from `resources` in that they represent dynamic operations that can modify state or interact with external systems.

The Tool API satisfies:
- **Discovery**: Clients can list available tools through the **`tools/list`** endpoint
- **Invocation**: Tools are called using the **`tools/call`** endpoint, where servers perform the requested operation and return results
- **Flexibility**: Tools can range from simple calculations to complex API interactions

## Tool definition Structure

```typescript
{
  name: string;          // Unique identifier for the tool
  description?: string;  // Human-readable description
  inputSchema: {         // JSON Schema for the tool's parameters
    type: "object",
    properties: { ... }  // Tool-specific parameters
  },
  annotations?: {        // Optional hints about tool behavior
    title?: string;      // Human-readable title for the tool
    readOnlyHint?: boolean;    // If true, the tool does not modify its environment
    destructiveHint?: boolean; // If true, the tool may perform destructive updates
    idempotentHint?: boolean;  // If true, repeated calls with same args have no additional effect
    openWorldHint?: boolean;   // If true, tool interacts with external entities
  }
}
```

### Typescript example

```typescript
const server = new Server({
  name: "example-server",
  version: "1.0.0"
}, {
  capabilities: {
    tools: {}
  }
});

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [{
      name: "calculate_sum",
      description: "Add two numbers together",
      inputSchema: {
        type: "object",
        properties: {
          a: { type: "number" },
          b: { type: "number" }
        },
        required: ["a", "b"]
      }
    }]
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "calculate_sum") {
    const { a, b } = request.params.arguments;
    return {
      content: [
        {
          type: "text",
          text: String(a + b)
        }
      ]
    };
  }
  throw new Error("Tool not found");
});
```
> WTF is required?

## Error handling
Tool errors should be reported within the result object, not as MCP protocol-level errors. This allows the LLM to see and potentially handle the error. When a tool encounters an error:

1. Set **`isError`** to **`true`** in the result
2. Include error details in the **`content`** array

Here’s an example of proper error handling for tools:

```typescript
try {
  // Tool operation
  const result = performOperation();
  return {
    content: [
      {
        type: "text",
        text: `Operation successful: ${result}`
      }
    ]
  };
} catch (error) {
  return {
    isError: true,
    content: [
      {
        type: "text",
        text: `Error: ${error.message}`
      }
    ]
  };
}
```

## **Tool annotations**

Tool annotations provide additional metadata about a tool’s behavior, helping clients understand how to present and manage tools. These annotations are hints that describe the nature and impact of a tool, but should not be relied upon for security decisions.

### **Purpose of tool annotations**

Tool annotations serve several key purposes:

1. Provide UX-specific information without affecting model context
2. Help clients categorize and present tools appropriately
3. Convey information about a tool’s potential side effects
4. Assist in developing intuitive interfaces for tool approval

### **Available tool annotations**

The MCP specification defines the following annotations for tools:

| **Annotation** | **Type** | **Default** | **Description** |
| --- | --- | --- | --- |
| **`title`** | string | - | A human-readable title for the tool, useful for UI display |
| **`readOnlyHint`** | boolean | false | If true, indicates the tool does not modify its environment |
| **`destructiveHint`** | boolean | true | If true, the tool may perform destructive updates (only meaningful when **`readOnlyHint`** is false) |
| **`idempotentHint`** | boolean | false | If true, calling the tool repeatedly with the same arguments has no additional effect (only meaningful when **`readOnlyHint`** is false) |
| **`openWorldHint`** | boolean | true | If true, the tool may interact with an “open world” of external entities |

### **Example usage**

Here’s how to define tools with annotations for different scenarios:

```typescript
// A read-only search tool
{
  name: "web_search",
  description: "Search the web for information",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string" }
    },
    required: ["query"]
  },
  annotations: {
    title: "Web Search",
    readOnlyHint: true,
    openWorldHint: true
  }
}

// A destructive file deletion tool
{
  name: "delete_file",
  description: "Delete a file from the filesystem",
  inputSchema: {
    type: "object",
    properties: {
      path: { type: "string" }
    },
    required: ["path"]
  },
  annotations: {
    title: "Delete File",
    readOnlyHint: false,
    destructiveHint: true,
    idempotentHint: true,
    openWorldHint: false
  }
}

// A non-destructive database record creation tool
{
  name: "create_record",
  description: "Create a new record in the database",
  inputSchema: {
    type: "object",
    properties: {
      table: { type: "string" },
      data: { type: "object" }
    },
    required: ["table", "data"]
  },
  annotations: {
    title: "Create Database Record",
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: false
  }
}
```

### Integrating annotations in server implementation

```typescript
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [{
      name: "calculate_sum",
      description: "Add two numbers together",
      inputSchema: {
        type: "object",
        properties: {
          a: { type: "number" },
          b: { type: "number" }
        },
        required: ["a", "b"]
      },
      annotations: {
        title: "Calculate Sum",
        readOnlyHint: true,
        openWorldHint: false
      }
    }]
  };
});
```