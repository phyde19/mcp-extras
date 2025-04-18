 # AI Agent Tooling Guidelines (2025+)

 ## 1. Minimal Glue Layers
 - Avoid heavy frameworks (e.g., LangChain-style “chains of everything”).
 - Use thin, explicit API clients for model and tool calls.
 - Keep call-site code clear: specify prompts, models, and options directly.

 ## 2. Explicit Orchestration
 - Represent agent steps as plain data structures (lists of tasks, JSON specs).
 - Implement each step as a simple function or class method for easy testing.
 - Orchestrate control flow in host language (e.g., Python) rather than an opaque engine.

 ## 3. Observability & Introspection
 - Stream prompts, responses, tool calls, retries, and errors to a telemetry backend.
 - Tag each message with trace IDs or request IDs for end-to-end tracking.
 - Provide sandboxed replay and hot-reload to accelerate iteration.

 ## 4. Composable Tools
 - Model “tools” as pure functions with typed inputs/outputs.
 - Import and pass function references instead of using complex plugin registries.
 - Version tools alongside agent code to maintain stable interfaces.

 ## 5. Lean Prompt Engineering
 - Use small, reusable templates with dynamic parameters.
 - Pre- and post-process data in code, not within bulky prompt wrappers.
 - Store templates separately (files or database) for easier updates.

 ## 6. Fail-Fast, Test-Driven Development
 - Unit-test each reasoning step by mocking LLM calls.
 - Simulate failure modes (timeouts, hallucinations) in CI.
 - Automate end-to-end smoke tests with fixed scenarios.

 ## 7. Cost Controls & Caching
 - Cache canonical prompt→response pairs in-memory or via a cache store.
 - Instrument token usage and apply budget guards in the orchestrator.
 - Surface cost telemetry ($/session) to stakeholders.

 ## 8. Lean SDK Design
 - If an SDK is needed, limit it to API client + logging modules.
 - Keep orchestration and business logic in application code to avoid dependency bloat.

 ## 9. Embrace Code + Data
 - Favor code-centric workflows over “no-code” for production agents.
 - Ensure full traceability by storing prompts, templates, and logs alongside code.

 ---

 *Compiled from industry teams (Anthropic, OpenAI, Windsurf, Cursor, Manus) insights on modern AI software architecture.*