# Prompts

Prompts offer another mechanism for servers (rather than clients) to adopt the responsibilty of defining and exposing useful artifacts for LLM applications.

> ℹ️ **Info**  
> Prompts are designed to be `user-controlled`, meaning they are exposed from servers to clients with the intention of the user being able to explicitly select them for use.

## **Overview**

Prompts in MCP are predefined templates that can:

- Accept dynamic arguments
- Include context from resources
- Chain multiple interactions
- Guide specific workflows
- Surface as UI elements (like slash commands)

## Prompt Structure

```typescript
{
  name: string;              // Unique identifier for the prompt
  description?: string;      // Human-readable description
  arguments?: [              // Optional list of arguments
    {
      name: string;          // Argument identifier
      description?: string;  // Argument description
      required?: boolean;    // Whether argument is required
    }
  ]
}
```

