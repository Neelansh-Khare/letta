# Letta Architecture

Letta is an open-source framework for building stateful LLM agents. Unlike stateless LLM calls, Letta agents maintain persistent memory (Core and Archival) and have an explicit lifecycle.

## High-Level Components

The system is composed of the following layers:

1.  **Interface Layer (API & Clients)**
    *   **REST API (`letta/server/rest_api`)**: A FastAPI server that exposes endpoints for managing agents, tools, blocks, and files.
    *   **WebSocket API**: Handles real-time streaming of agent thoughts and responses.
    *   **CLI (`letta/cli`)**: Command-line interface for interacting with the server.
    *   **ADE (Agent Development Environment)**: A React-based frontend (hosted or local) that connects to the API.

2.  **Service Layer (`letta/services`)**
    *   Acts as the intermediary between the API and the Core Logic/Database.
    *   Handles orchestration (e.g., `AgentService` loading an agent from the DB and initializing the `LettaAgent` class).

3.  **Core Logic (The "Brain")**
    *   **`LettaAgent` (`letta/agent.py`)**: The runtime object representing an active agent. It holds the context window and executes the "Step" loop.
    *   **Context Window Management**: Manages what data (System Instructions, Core Memory, Recent History) fits into the LLM's limited context.

4.  **Memory Systems (`letta/memory.py`)**
    *   **Core Memory**: In-context, editable memory blocks (e.g., `persona`, `human`). The agent can edit this via tools.
    *   **Archival Memory**: Long-term storage backed by a Vector Database (pgvector). Used for retrieving relevant passages.

5.  **Storage Layer**
    *   **PostgreSQL**: Stores relational data (Agents, Users, Runs, Tool Definitions).
    *   **pgvector**: Stores embeddings for Archival Memory.

---

## The "Step" Loop

The heart of Letta is the `step()` function in `letta/agent.py`. This loop drives the agent's behavior.

1.  **Input**: The agent receives a `UserMessage` or a System Event (e.g., Heartbeat).
2.  **Context Construction**: Letta assembles the context window:
    *   System Prompt (Instructions + Core Memory blocks).
    *   Retrieved Context (from Archival Memory, if applicable).
    *   Message History (sliding window of recent chat).
3.  **LLM Call**: The assembled context is sent to the LLM (OpenAI, Anthropic, or Local).
4.  **Parse**: The LLM's response is parsed. It typically contains:
    *   **Internal Monologue (Thoughts)**: The agent "thinking" to itself.
    *   **Tool Call (Function)**: A request to execute a function (e.g., `send_message`, `core_memory_replace`).
5.  **Tool Execution**:
    *   If a tool is called, Letta executes the corresponding Python function.
    *   The *output* of the tool is fed back into the context window as a `ToolMessage`.
6.  **Loop**: The cycle repeats (Heartbeat) until the agent decides to stop (usually by sending a final response to the user).

---

## Deep Dive: Functions (Tools)

In Letta, "Tools" are Python functions that the LLM can invoke. They bridge the gap between the stochastic LLM and deterministic code.

### 1. Function Definition

Tools are defined as standard Python functions with **Google-style docstrings**. Letta uses these docstrings to generate the JSON Schema required by the LLM.

**Example Tool (`letta/functions/example.py`):**

```python
def roll_dice(num_sides: int = 6):
    """
    Rolls a die with a specified number of sides.

    Args:
        num_sides (int): The number of sides on the die. Defaults to 6.

    Returns:
        int: The result of the roll.
    """
    import random
    return random.randint(1, num_sides)
```

### 2. Schema Generation (`letta/functions/schema_generator.py`)

Letta includes a parser that reads the Python source code (via `ast` module) and auto-generates the OpenAI-compatible JSON schema.

*   **Inputs**: Source code of the function.
*   **Process**:
    1.  Parse AST (Abstract Syntax Tree).
    2.  Extract function name, docstring, and type hints.
    3.  Map Python types (`str`, `int`, `Optional`) to JSON Schema types.
*   **Output**: A JSON dictionary describing the tool to the LLM.

### 3. Core Tools vs. User Tools

*   **Core Tools**: Built-in functions that every Letta agent has.
    *   `send_message`: Sends a response to the user.
    *   `core_memory_append`: Adds information to a memory block.
    *   `core_memory_replace`: Updates a memory block.
    *   `archival_memory_insert`: Saves data to long-term storage.
    *   `archival_memory_search`: Retrieves data from long-term storage.
*   **User Tools**: Custom functions added by the user (like the `roll_dice` example above).

### 4. Execution Flow

When an agent triggers a tool:
1.  **Detection**: The `step` loop detects a `function_call` in the LLM response.
2.  **Resolution**: It looks up the function name in the agent's `toolbox`.
3.  **Invocation**:
    *   Arguments provided by the LLM are validated against the schema.
    *   The Python function is executed safely.
4.  **Feedback**: The return value (stringified) is added to the chat history as a `function` role message.
5.  **Heartbeat**: A "Heartbeat" system message is often triggered immediately after a tool execution, prompting the agent to decide what to do next with this new information (e.g., tell the user the result).
