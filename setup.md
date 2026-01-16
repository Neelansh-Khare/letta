# Development Setup Guide for Letta

This guide outlines the steps to set up the Letta repository for development on macOS.

## Prerequisites

-   Python 3.11+ (Detected: 3.13.1)
-   PostgreSQL (Running locally)
-   `uv` (Python package manager) - *To be installed*

## Setup Steps

### 1. Install `uv`

We will install `uv` to manage Python dependencies and virtual environments efficiently.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Configure PostgreSQL

We will set up the `letta` user and database on your local PostgreSQL instance.

```sql
-- Run in psql
CREATE ROLE letta WITH LOGIN SUPERUSER PASSWORD 'letta';
CREATE DATABASE letta OWNER letta;
\c letta
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Initialize Python Environment

We will use `uv` to create a virtual environment and install dependencies.

```bash
uv venv
source .venv/bin/activate
uv sync --all-extras
```

### 4. Configure Environment Variables

We need to tell Letta where the database is.

```bash
export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"
```

### 5. Run Database Migrations

Apply the database schema changes using Alembic.

```bash
uv run alembic upgrade head
```

### 6. Verify Installation



Run the server or a test to ensure everything is working.



```bash

uv run letta server

```



To run tests that require external LLM providers, set the appropriate environment variables:



```bash

export ANTHROPIC_API_KEY="sk-..."

export OPENAI_API_KEY="sk-..."

uv run pytest tests/test_server.py

```

✦ Yes, the repository is now set up for both development and local use.

  🛠 For Development (Contributing)
   * Isolated Environment: uv is installed, and a virtual environment (.venv) has been created with all development extras (uv sync --all-extras).
   * Database: A local PostgreSQL instance is running with the pgvector extension. The schema is fully up-to-date (all alembic migrations
     applied).
   * Editable Install: The letta package is installed in editable mode, so any changes you make to the source code are reflected immediately when
     running the server or tests.
   * Verified: Running uv run pytest tests/test_server.py confirmed the core server logic is functional.

  🚀 For Local Use (User)
   * Starting the Server: You can launch your own Letta server immediately using the local Python environment:
   1     export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"
   2     uv run letta server
   * Accessing the UI: When the server starts, it will provide a link (typically https://app.letta.com/development-servers/local/dashboard) to the
     Agent Development Environment (ADE), which will connect to your local server.
   * Docker Option: If you prefer a fully containerized setup later, the compose.yaml is ready. You just need to run docker compose up.

  📝 Next Steps
  I have summarized these instructions in the `setup.md` file in the root of the repository. You can refer to it anytime to restart the
  environment or the database.
