# Using Letta Locally

This guide covers how to use Letta for local development, including running the server, using the CLI, and connecting local models (Ollama/vLLM) or external APIs like Gemini.

## Prerequisites

Ensure you have the following installed:
*   **PostgreSQL**: Running locally (default port 5432).
*   **uv**: Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

## Quick Start

### 1. Start the Server
The central hub of Letta is the API server.

```bash
# Ensure DB environment variable is set (add to .bashrc/.zshrc for persistence)
export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"

# Run the server
uv run letta server
```

### 2. Connect the Interface (ADE)
Letta uses a hosted frontend (Agent Development Environment) that connects to your local server.

1.  Open your browser to: `https://app.letta.com/development-servers/local/dashboard`
2.  If prompted, ensure it's pointing to `http://localhost:8283`.
3.  You can now create agents, view memory, and chat visually.

---

## CLI Usage

For headless interactions or scripting, use the CLI.

```bash
# Check status
uv run letta status

# List agents
uv run letta list agents

# Chat with an agent in the terminal
# (You'll need to create one first via UI or `letta create`)
uv run letta agent interactive <agent_name>
```

---

## Using Local Models (MacBook Air / Apple Silicon)

Your MacBook Air (especially with M1/M2/M3 chips) is highly capable of running local models. Letta works seamlessly with **Ollama**, which is optimized for Apple Silicon.

### 1. Setup Ollama
Download [Ollama for macOS](https://ollama.com/download). It uses the GPU (Metal) automatically.

```bash
# Pull a model (Llama 3 is a great balance of speed/quality for 8GB+ RAM)
ollama pull llama3

# Pull an embedding model (Required for Letta memory)
ollama pull nomic-embed-text
```

### 2. Configure Letta
Point Letta to your local Ollama instance.

```bash
uv run letta configure \
  --endpoint "http://localhost:11434" \
  --endpoint-type "ollama" \
  --model "llama3" \
  --context-window 8192 \
  --embedding-endpoint "http://localhost:11434" \
  --embedding-endpoint-type "ollama" \
  --embedding-model "nomic-embed-text" \
  --embedding-dim 768
```

---

## Using Google Gemini API

Letta has first-class support for Google's Gemini models (Flash, Pro). This is a great alternative if you want higher intelligence than local models but lower cost than GPT-4.

### 1. Get an API Key
Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Set the Environment Variable
Export your key before starting the server:

```bash
export GEMINI_API_KEY="your-key-here"
```

### 3. Configure Letta
You can configure a new agent to use Gemini.

**Via CLI:**
```bash
# Create a new agent using Gemini Pro
uv run letta create \
  --name "gemini-agent" \
  --model "gemini-1.5-pro-latest" \
  --endpoint-type "google_ai" \
  --context-window 2000000
```

**Via ADE (UI):**
1.  Go to **Settings** -> **LLM Providers**.
2.  Select **Google AI** (it may auto-detect your key if set in env, otherwise input it).
3.  Create an agent and select `gemini-1.5-pro` or `gemini-1.5-flash` from the dropdown.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'letta'"
This happens if the python environment isn't linking to the source correctly.
**Fix:** Run `uv pip install -e .` in the root directory.

### Database Connection Failures
**Fix:** Ensure Postgres is running and the `LETTA_PG_URI` is correct.
```bash
psql -h localhost -U letta -d letta
```

### Context Window Errors
If using local models, ensure the `context_window` setting matches the model's capability (e.g., 8192 for Llama 3). If set too high, the model will crash or produce garbage.

```
```