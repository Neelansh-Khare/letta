# Letta Local Development & Contribution Guide

This guide covers everything you need to know about running Letta locally with Ollama and contributing to the project.

---

## ✅ What You've Accomplished

- [x] Set up PostgreSQL database with pgvector extension
- [x] Installed dependencies with `uv`
- [x] Configured Ollama with local models (llama3.1, nomic-embed-text)
- [x] Generated HTTPS certificates with mkcert
- [x] Connected the web UI to your local Letta server
- [x] Successfully running at `https://localhost:8283`

---

## 🗺️ Codebase Structure Overview

### Key Directories

```
letta/
├── agents/          # Agent logic and execution engine
├── server/          # REST API server (FastAPI)
│   └── rest_api/    # API routes, middleware, app setup
├── schemas/         # Data models (Pydantic schemas)
│   └── providers/   # Provider implementations (Ollama, OpenAI, etc.)
├── services/        # Business logic layer
│   ├── provider_manager.py  # Provider/model management
│   ├── agent_manager.py     # Agent CRUD operations
│   └── tool_manager.py      # Tool management
├── llm_api/         # LLM client implementations
├── orm/             # Database models (SQLAlchemy ORM)
├── functions/       # Built-in tools/functions for agents
├── cli/             # CLI commands
├── constants.py     # Configuration constants
└── errors.py        # Custom exception definitions
```

### Important Files You Interacted With

- **`letta/server/rest_api/app.py:764-776`** - HTTPS setup with certificates
- **`letta/services/provider_manager.py`** - Ollama provider sync logic
- **`letta/schemas/providers/ollama.py`** - Ollama provider implementation
- **`letta/settings.py:200-212`** - CORS configuration

---

## 🧪 Testing Your Setup

### Create Your First Agent with Ollama

1. **Open the web UI**: https://app.letta.com/development-servers/local/dashboard

2. **Create a new agent**:
   - Click **"New Agent"** or **"Create Agent"**
   - **Name**: `test-ollama-agent`
   - **LLM Model**: `ollama/llama3.1:latest`
   - **Embedding Model**: `ollama/nomic-embed-text:latest`
   - **Memory Blocks**: Keep defaults (human + persona)

3. **Test the agent**:
   - Send: *"Tell me what you remember about me"*
   - Send: *"Create a list of 3 random cities"*
   - Observe how it uses memory and tools

### What This Tests

- ✅ Ollama integration works
- ✅ Agent creation and persistence
- ✅ Memory block functionality
- ✅ Message streaming
- ✅ Tool execution

---

## 🔧 Development Workflow

### 1. Set Up Your Environment

```bash
# Navigate to the project
cd /Users/neelanshkhare/Desktop/NeelanshDesktop/Professional/SideProjects/letta

# Activate virtual environment
source .venv/bin/activate

# Install pre-commit hooks (IMPORTANT!)
uv run pre-commit install

# Test pre-commit
uv run pre-commit run --all-files
```

### 2. Start the Development Server

```bash
# Set environment variables
export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"
export OLLAMA_BASE_URL="http://localhost:11434"

# Start server with HTTPS
uv run --env-file .env letta server --localhttps

# Or without HTTPS (simpler, but web UI requires HTTPS)
# uv run --env-file .env letta server
```

### 3. Making Changes

#### Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

#### Make Your Changes

Edit files as needed. Common patterns:

- **Adding a new API endpoint**: `letta/server/rest_api/routers/v1/`
- **Adding business logic**: `letta/services/`
- **Modifying schemas**: `letta/schemas/`
- **Database changes**: `letta/orm/`

#### Format Your Code

```bash
# Format with black (required before committing)
uv run black . -l 140

# Or let pre-commit handle it
git add .
git commit -m "feat: your feature description"
# pre-commit will run automatically
```

### 4. Testing

```bash
# Run all tests
uv run pytest -s tests

# Run specific test file
uv run pytest tests/test_server.py -v

# Run tests matching a pattern
uv run pytest -k "test_agent" -v

# Run with coverage
uv run pytest --cov=letta tests/
```

### 5. Database Migrations

If you modify database models:

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Add field to agent table"

# Review the generated migration in alembic/versions/

# Apply the migration
uv run alembic upgrade head

# Rollback if needed
uv run alembic downgrade -1
```

### 6. Submit Your Contribution

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a pull request (install gh CLI if needed)
gh pr create --title "feat: your feature description" --body "Description of changes"

# Or create PR manually on GitHub
open https://github.com/letta-ai/letta/compare
```

---

## 🎯 Finding Contribution Areas

### Browse Issues on GitHub

```bash
# Install GitHub CLI
brew install gh
gh auth login

# Find good first issues
gh issue list --label "good first issue" --limit 20

# Find issues by topic
gh issue list --label "enhancement,ollama" --limit 10

# Find bugs
gh issue list --label "bug" --state open --limit 20
```

### Recommended Areas Based on Your Setup

#### 1. **Ollama Provider Enhancements**
**Files**: `letta/schemas/providers/ollama.py`, `letta/llm_api/`

**Ideas**:
- Add support for Ollama's vision capabilities
- Improve model capability detection (line 78-80)
- Better error messages when models aren't available
- Add support for Ollama's "thinking" mode models
- Improve context window detection logic

#### 2. **Provider Management**
**Files**: `letta/services/provider_manager.py`

**Ideas**:
- Better error handling for failed provider syncs (line 550)
- Add retry logic for provider API calls
- Improve logging for debugging provider issues
- Add provider health checks

#### 3. **API Improvements**
**Files**: `letta/server/rest_api/routers/`

**Ideas**:
- Add new endpoints for missing functionality
- Improve API documentation/examples
- Add request validation
- Better error responses

#### 4. **Testing**
**Files**: `tests/`

**Ideas**:
- Add tests for Ollama provider
- Integration tests for agent creation
- API endpoint tests
- Provider sync tests

#### 5. **Documentation**
**Files**: `*.md`, docstrings in Python files

**Ideas**:
- Improve local setup instructions
- Add troubleshooting guides
- Document provider configuration
- Add code examples

#### 6. **Developer Experience**
**Ideas**:
- Improve error messages
- Add helpful logging
- Better validation messages
- Setup automation scripts

---

## 📚 Learning the Codebase

### Trace a Feature: Agent Creation

Follow the request flow:

1. **API Endpoint** → `letta/server/rest_api/routers/v1/agents.py`
   - Look for `@router.post("/")` or `create_agent`

2. **Service Layer** → `letta/services/agent_manager.py`
   - Business logic for creating agents
   - Validation, defaults, initialization

3. **Database Layer** → `letta/orm/agent.py`
   - SQLAlchemy model definition
   - Persistence logic

4. **Schemas** → `letta/schemas/agent.py`
   - Pydantic models for validation
   - API request/response types

### Trace a Feature: Message Handling

1. **API** → `letta/server/rest_api/routers/v1/agents.py` (messages endpoint)
2. **Agent Logic** → `letta/agent.py` or `letta/agents/`
3. **LLM Client** → `letta/llm_api/openai_client.py` (used for Ollama too!)
4. **Tool Execution** → `letta/functions/`

### Debugging Tips

```bash
# Enable debug mode
export LETTA_DEBUG=true
uv run --env-file .env letta server --debug

# Check logs
tail -f ~/.letta/logs/letta.log  # if logging to file

# Use Python debugger
# Add to code: import pdb; pdb.set_trace()
```

---

## 🚀 Next Steps & Action Plan

### Week 1: Explore & Learn

- [ ] **Create and test an agent with Ollama** (see above)
- [ ] **Join the community**:
  - [Discord](https://discord.gg/letta) - Introduce yourself!
  - [Forum](https://forum.letta.com/) - Browse discussions
- [ ] **Read code**:
  - Pick a feature you used in the UI
  - Trace it through the codebase
  - Understand the request flow
- [ ] **Run the test suite**:
  ```bash
  uv run pytest tests/ -v
  ```

### Week 2: Find Your First Issue

- [ ] **Browse issues**:
  ```bash
  gh issue list --label "good first issue"
  ```
- [ ] **Pick something small**:
  - Documentation improvement
  - Error message enhancement
  - Add a test
  - Fix a typo
- [ ] **Ask questions**:
  - Comment on the issue to claim it
  - Ask for clarification on Discord
  - Understand the context

### Week 3: Make Your First Contribution

- [ ] **Create a branch**: `git checkout -b feature/your-fix`
- [ ] **Make the change**: Small, focused, well-tested
- [ ] **Write tests**: If applicable
- [ ] **Format code**: `uv run black .`
- [ ] **Create PR**: Include description, screenshots if UI change
- [ ] **Respond to feedback**: Be open to suggestions

### Ongoing

- [ ] **Stay engaged**:
  - Check Discord regularly
  - Review other PRs
  - Help answer questions
- [ ] **Level up**:
  - Take on bigger issues
  - Propose new features
  - Improve architecture
- [ ] **Share knowledge**:
  - Write blog posts
  - Give talks
  - Help other contributors

---

## 💡 Pro Tips

### General

1. **Use the debugger**: Set breakpoints in VS Code/PyCharm to understand request flow
2. **Check the logs**: Server logs show exactly what's happening
3. **Ask questions early**: Discord is very active and helpful
4. **Start small**: Don't refactor everything at once
5. **Read existing PRs**: Learn from how others structure contributions

### Code Quality

1. **Follow the style guide**: Black handles formatting, but write clean code
2. **Write descriptive commits**: Use conventional commits (`feat:`, `fix:`, `docs:`)
3. **Add docstrings**: Help others understand your code
4. **Test your changes**: Both manually and with automated tests
5. **Keep PRs focused**: One feature/fix per PR

### Communication

1. **Update issues**: Comment on progress
2. **Link PRs to issues**: Use "Closes #123" in PR description
3. **Respond to reviews**: Be receptive to feedback
4. **Document decisions**: Explain why, not just what
5. **Be patient**: Reviews may take time

---

## 🛠️ Common Development Tasks

### Restart Server After Changes

```bash
# Kill with Ctrl+C, then restart
uv run --env-file .env letta server --localhttps
```

### Check Your Changes

```bash
# See what files changed
git status

# See the diff
git diff

# See staged changes
git diff --cached
```

### Working with Git

```bash
# Create a new branch
git checkout -b feature/my-feature

# Stage changes
git add letta/schemas/agent.py

# Commit with message
git commit -m "feat: add new field to agent schema"

# Push to GitHub
git push origin feature/my-feature

# Update your branch with main
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main
```

### Database Tasks

```bash
# Reset database (careful!)
psql -U letta -d letta -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
uv run alembic upgrade head

# View current migration
uv run alembic current

# View migration history
uv run alembic history
```

### Check Ollama Models

```bash
# List available models
curl http://localhost:11434/api/tags | python3 -m json.tool

# Check model details
curl http://localhost:11434/api/show -d '{"name": "llama3.1:latest"}' | python3 -m json.tool

# Pull a new model
ollama pull llama3.2:latest
```

---

## 🔗 Important Links

- **Main Repo**: https://github.com/letta-ai/letta
- **Documentation**: https://docs.letta.com
- **Discord**: https://discord.gg/letta
- **Forum**: https://forum.letta.com
- **Twitter**: https://twitter.com/Letta_AI
- **Contributing Guide**: `CONTRIBUTING.md` in repo

---

## 🐛 Troubleshooting

### Server Won't Start

```bash
# Check if PostgreSQL is running
psql -U letta -d letta -c "SELECT 1;"

# Check if port is in use
lsof -i :8283

# Check Ollama is running
curl http://localhost:11434/api/tags
```

### Certificate Issues

```bash
# Regenerate certificates
cd certs
rm localhost.pem localhost-key.pem
mkcert localhost 127.0.0.1 ::1
mv localhost+2.pem localhost.pem
mv localhost+2-key.pem localhost-key.pem

# Trust the CA
mkcert -install
```

### Database Issues

```bash
# Check connection
psql -U letta -d letta -c "SELECT version();"

# Run migrations
uv run alembic upgrade head

# Check migration status
uv run alembic current
```

### Pre-commit Failures

```bash
# Run black manually
uv run black . -l 140

# Skip pre-commit (not recommended)
git commit --no-verify -m "message"

# Update pre-commit hooks
uv run pre-commit autoupdate
```

---

## 📝 Notes

### Your Current Setup

- **Database**: PostgreSQL at `localhost:5432/letta`
- **Server**: `https://localhost:8283`
- **Ollama**: `http://localhost:11434`
- **Models**:
  - LLM: `llama3.1:latest`
  - Embedding: `nomic-embed-text:latest`

### Environment Variables

Keep these in your `.env` file or shell profile:

```bash
export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"
export OLLAMA_BASE_URL="http://localhost:11434"
```

---

**Good luck with your contributions! 🚀**

Remember: Every expert was once a beginner. Start small, ask questions, and have fun!