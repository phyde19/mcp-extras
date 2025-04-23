## Wire-Level Schemas for Tool / Function Calling

This document outlines the wire-level request and response schemas used for tool/function calling by Claude 3 Sonnet (Anthropic), GPT-4o (OpenAI), and Gemini 2.0 Flash (Google).

---

## 1. Claude 3 Sonnet 3.7 (Anthropic Messages API)

**Request (JSON body):**

```jsonc
POST https://api.anthropic.com/v1/messages
Authorization: Bearer $ANTHROPIC_API_KEY
anthropic-version: 2023-10-01

{
  "model": "claude-3-7-sonnet-20250219",
  "max_tokens": 1024,
  "messages": [
    { "role": "user", "content": "What’s the weather in San Francisco?" }
  ],
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather in a given location",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": { "type": "string" },
          "unit": { "type": "string", "enum": ["celsius","fahrenheit"] }
        },
        "required": ["location"]
      }
    }
  ],
  "tool_choice": { "type": "auto" }
}
```

**Assistant response:**

```json
{
  "id": "msg_...",
  "model": "claude-3-7-sonnet-20250219",
  "role": "assistant",
  "stop_reason": "tool_use",
  "content": [
    { "type": "text", "text": "<thinking>…</thinking>" },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "get_weather",
      "input": { "location": "San Francisco, CA", "unit": "celsius" }
    }
  ]
}
```

**Returning results:**

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "15 °C"
    }
  ]
}
```

---

## 2. GPT-4o (OpenAI Chat Completions API)

**Request (JSON body):**

```jsonc
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer $OPENAI_API_KEY

{
  "model": "gpt-4o-2024-05-13",
  "messages": [
    { "role": "user", "content": "What’s the weather in San Francisco?" }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather",
        "parameters": {
          "type": "object",
          "properties": {
            "location": { "type": "string" },
            "unit": { "type": "string", "enum": ["celsius","fahrenheit"] }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

**Assistant response:**

```json
{
  "id": "chatcmpl_...",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abcd1234",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\":\"San Francisco, CA\",\"unit\":\"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

**Returning results:**

```json
{
  "role": "tool",
  "tool_call_id": "call_abcd1234",
  "name": "get_weather",
  "content": "{\"temperature\":15,\"unit\":\"C\"}"
}
```

---

## 3. Gemini 2.0 Flash (Google Gemini API v1beta)

**Request (JSON body):**

```jsonc
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$API_KEY

{
  "contents": [
    { "role": "user",
      "parts": [{ "text": "Turn the lights down to a romantic level" }] }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "set_light_values",
          "description": "Sets brightness and color temperature of a light.",
          "parameters": {
            "type": "object",
            "properties": {
              "brightness": { "type": "integer" },
              "color_temp": { "type": "string", "enum": ["daylight","cool","warm"] }
            },
            "required": ["brightness", "color_temp"]
          }
        }
      ]
    }
  ],
  "toolConfig": { "functionCallingConfig": { "mode": "AUTO" } }
}
```

**Model response:**

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          { "functionCall": {
              "name": "set_light_values",
              "args": { "brightness": 25, "color_temp": "warm" }
          }}
        ]
      },
      "finishReason": "FUNCTION_CALL"
    }
  ]
}
```

**Returning results:**

```json
{
  "role": "user",
  "parts": [
    { "functionResponse":{
        "name":"set_light_values",
        "response":{ "result": { "brightness":25,"colorTemperature":"warm"} }
    }}
  ]
}
```
..

..

# Tool responses differences 

### Tool Call Lifecycle for Claude Sonnet 3.7

```python
follow_up_request = {
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": "What's the current weather in San Francisco?"
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": tool_use_id,
                    "name": tool_name,
                    "input": tool_input
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": tool_result
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=follow_up_request)
final_response = response.json()
print(json.dumps(final_response, indent=2))
```


### Tool Call Lifecycle in OpenAI GPT-4o

Here's how the equivalent step looks for OpenAI's GPT-4o API:
 
 ```python
import requests
import json

API_KEY = "your_openai_api_key"
url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

follow_up_request = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": "What's the current weather in San Francisco?"
        },
        {
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": "get_weather",
                "arguments": json.dumps({"location": "San Francisco"})
            }
        },
        {
            "role": "function",
            "name": "get_weather",
            "content": json.dumps({
                "temperature": 62,
                "condition": "Foggy",
                "humidity": 78,
                "wind": "10 mph"
            })
        }
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or location"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
}

response = requests.post(url, headers=headers, json=follow_up_request)
final_response = response.json()
print(json.dumps(final_response, indent=2))

 ```

## Tool Call Lifecycle in Google Gemini 2.0 Flash
Here's how the equivalent step looks for Google's Gemini 2.0 Flash API:

```python
import requests
import json

API_KEY = "your_gemini_api_key"
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

headers = {
    "Content-Type": "application/json"
}

follow_up_request = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {
                    "text": "What's the current weather in San Francisco?"
                }
            ]
        },
        {
            "role": "model",
            "parts": [
                {
                    "functionCall": {
                        "name": "get_weather",
                        "args": {
                            "location": "San Francisco"
                        }
                    }
                }
            ]
        },
        {
            "role": "function",
            "parts": [
                {
                    "functionResponse": {
                        "name": "get_weather",
                        "response": {
                            "temperature": 62,
                            "condition": "Foggy",
                            "humidity": 78,
                            "wind": "10 mph"
                        }
                    }
                }
            ]
        }
    ],
    "tools": [
        {
            "functionDeclarations": [
                {
                    "name": "get_weather",
                    "description": "Get current weather for a location",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "location": {
                                "type": "STRING",
                                "description": "City name or location"
                            }
                        },
                        "required": ["location"]
                    }
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.9,
        "maxOutputTokens": 1024
    }
}

url_with_key = f"{url}?key={API_KEY}"
response = requests.post(url_with_key, headers=headers, json=follow_up_request)
final_response = response.json()
print(json.dumps(final_response, indent=2))
```