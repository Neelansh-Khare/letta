# Development Setup Guide for Letta

This guide provides step-by-step instructions for setting up the Letta repository for local development and use with Ollama on both Windows and macOS.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Platform-Specific Setup](#platform-specific-setup)
  - [Windows Setup](#windows-setup)
  - [macOS Setup](#macos-setup)
- [Common Setup Steps](#common-setup-steps)
- [Ollama Configuration](#ollama-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Both Platforms

- **Python 3.11-3.13** (Python 3.14+ is not yet supported)
- **PostgreSQL** with pgvector extension
- **uv** (Python package manager)
- **Ollama** (for local LLM inference)

### Windows-Specific

- **Windows 10/11** (64-bit)
- **PowerShell** or **Command Prompt** (PowerShell recommended)
- **Git for Windows** (https://git-scm.com/download/win)

### macOS-Specific

- **macOS 10.15+** (Catalina or later)
- **Homebrew** package manager (https://brew.sh)
- **Xcode Command Line Tools** (`xcode-select --install`)

---

## Platform-Specific Setup

### Windows Setup

#### 1. Install PostgreSQL

**Option A: Using Official Installer (Recommended)**

1. Download from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the wizard:
   - Choose a password for the `postgres` user
   - Keep default port: **5432**
   - Install the pgvector extension after PostgreSQL is installed

**Option B: Using Scoop**

```powershell
# Install Scoop if not already installed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

# Install PostgreSQL
scoop install postgresql
```

**Install pgvector Extension**

```powershell
# Download pgvector from: https://github.com/pgvector/pgvector/releases
# Extract and follow Windows installation instructions, or use pre-built binaries
```

#### 2. Configure PostgreSQL

Open **PowerShell** or **Command Prompt** as Administrator:

```powershell
# Start PostgreSQL service (if not auto-started)
pg_ctl -D "C:\Program Files\PostgreSQL\16\data" start

# Connect to PostgreSQL
psql -U postgres

# Run these SQL commands in the psql prompt:
CREATE ROLE letta WITH LOGIN SUPERUSER PASSWORD 'letta';
CREATE DATABASE letta OWNER letta;
\c letta
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### 3. Install `uv`

```powershell
# Install uv using the official installer
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Restart your terminal or refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

#### 4. Install Ollama

1. Download Ollama for Windows: https://ollama.com/download/windows
2. Run the installer
3. Verify installation:

```powershell
ollama --version
```

4. Pull recommended models:

```powershell
# LLM model (choose one based on your system RAM)
ollama pull llama3.1           # ~4GB RAM (recommended for 8GB+ systems)
# OR
ollama pull llama3.2:latest    # ~2GB RAM (for 4-8GB systems)
# OR
ollama pull qwen2.5:latest     # ~4GB RAM (alternative)

# Embedding model (required for memory)
ollama pull nomic-embed-text
```

#### 5. Set Environment Variables (Windows)

**Option A: Persistent (Recommended)**

```powershell
# Set environment variables permanently
[System.Environment]::SetEnvironmentVariable('LETTA_PG_URI', 'postgresql://letta:letta@localhost:5432/letta', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_BASE_URL', 'http://localhost:11434', 'User')

# Refresh current session
$env:LETTA_PG_URI = "postgresql://letta:letta@localhost:5432/letta"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
```

**Option B: Session-Only**

```powershell
$env:LETTA_PG_URI = "postgresql://letta:letta@localhost:5432/letta"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
```

**Option C: Create `.env` file (Recommended for development)**

Create a `.env` file in the project root:

```env
LETTA_PG_URI=postgresql://letta:letta@localhost:5432/letta
OLLAMA_BASE_URL=http://localhost:11434
```

---

### macOS Setup

#### 1. Install PostgreSQL

**Using Homebrew (Recommended)**

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL with pgvector
brew install postgresql@16 pgvector

# Start PostgreSQL service
brew services start postgresql@16

# Or start manually (non-persistent)
pg_ctl -D /opt/homebrew/var/postgresql@16 start
```

#### 2. Configure PostgreSQL

```bash
# Connect to PostgreSQL (no password needed for local Homebrew install)
psql postgres

# Run these SQL commands:
CREATE ROLE letta WITH LOGIN SUPERUSER PASSWORD 'letta';
CREATE DATABASE letta OWNER letta;
\c letta
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### 3. Install `uv`

```bash
# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.zshrc or ~/.bashrc for persistence)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell configuration
source ~/.zshrc  # or source ~/.bashrc
```

#### 4. Install Ollama

```bash
# Download and install Ollama for macOS
# Option A: Direct download from https://ollama.com/download/mac

# Option B: Using Homebrew
brew install ollama

# Start Ollama service
brew services start ollama

# Or run manually
ollama serve
```

In a new terminal, pull models:

```bash
# LLM model (llama3.1 recommended for M1/M2/M3 Macs)
ollama pull llama3.1           # ~4GB, optimized for Apple Silicon
# OR
ollama pull llama3.2:latest    # ~2GB, faster but less capable
# OR
ollama pull qwen2.5:latest     # ~4GB, strong alternative

# Embedding model (required)
ollama pull nomic-embed-text
```

#### 5. Set Environment Variables (macOS)

**Option A: Persistent (Recommended)**

```bash
# Add to ~/.zshrc (zsh) or ~/.bashrc (bash)
echo 'export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"' >> ~/.zshrc
echo 'export OLLAMA_BASE_URL="http://localhost:11434"' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

**Option B: Create `.env` file (Recommended for development)**

Create a `.env` file in the project root:

```bash
cat > .env << EOF
LETTA_PG_URI=postgresql://letta:letta@localhost:5432/letta
OLLAMA_BASE_URL=http://localhost:11434
EOF
```

---

## Common Setup Steps

These steps are identical for both Windows and macOS.

### 1. Clone the Repository

```bash
git clone https://github.com/letta-ai/letta.git
cd letta
```

### 2. Initialize Python Environment with `uv`

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
# On macOS/Linux:
source .venv/bin/activate

# Install all dependencies
uv sync --all-extras
```

### 3. Run Database Migrations

```bash
uv run alembic upgrade head
```

### 4. Install Pre-commit Hooks (Optional but Recommended)

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## Ollama Configuration

### Verify Ollama is Running

**Windows:**
```powershell
# Check if Ollama service is running
ollama list

# Test connection
curl http://localhost:11434/api/tags
```

**macOS:**
```bash
# Check if Ollama is running
ollama list

# Test connection
curl http://localhost:11434/api/tags
```

### Configure Letta to Use Ollama

Letta will automatically detect Ollama if the `OLLAMA_BASE_URL` environment variable is set. When you create an agent via the UI or API, you'll be able to select Ollama models.

**Alternative: Configure via CLI**

```bash
# This is optional - the server will auto-discover Ollama models
uv run letta configure \
  --endpoint "http://localhost:11434" \
  --endpoint-type "ollama" \
  --model "llama3.1:latest" \
  --embedding-endpoint "http://localhost:11434" \
  --embedding-endpoint-type "ollama" \
  --embedding-model "nomic-embed-text"
```

---

## Local HTTPS Setup (for Letta ADE)

To connect your local Letta server to the hosted Agent Development Environment (ADE) at `app.letta.com`, you must use HTTPS. This requires generating locally-trusted SSL certificates.

### 1. Install `mkcert`

**macOS:**
```bash
brew install mkcert
mkcert -install
```

**Windows (PowerShell):**
```powershell
# Using Scoop
scoop install mkcert
mkcert -install

# OR Download the binary from https://github.com/FiloSottile/mkcert/releases
```

### 2. Generate Certificates

Run these commands from the root of the `letta` repository to create the `certs` directory and generate the necessary files:

```bash
# Create certs directory
mkdir -p certs

# Generate certificates for localhost
mkcert -cert-file certs/localhost.pem -key-file certs/localhost-key.pem localhost
```

### 3. Enable HTTPS in Letta

When starting the server, you must set the `LOCAL_HTTPS` environment variable to `true`. This tells Letta to look for the certificates in the `certs/` folder and start the server on `https://localhost:8283`.

---

## Verification

### 1. Start the Letta Server

**Windows (PowerShell):**
```powershell
# Make sure environment variables are set
$env:LETTA_PG_URI = "postgresql://letta:letta@localhost:5432/letta"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:LOCAL_HTTPS = "true"  # Enable HTTPS for ADE connection

# Start server
uv run letta server
```

**macOS:**
```bash
# Make sure environment variables are set
export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"
export OLLAMA_BASE_URL="http://localhost:11434"
export LOCAL_HTTPS="true"  # Enable HTTPS for ADE connection

# Start server
uv run letta server
```

### 2. Access the Web UI

1. Open your browser to: [https://app.letta.com/development-servers/local/dashboard](https://app.letta.com/development-servers/local/dashboard)
2. Click **"Add remote server"** (if not already connected).
3. Enter the URL: `https://localhost:8283`
4. Leave the password blank (unless you configured one).
5. **Note:** If you see a "Connection Refused" or SSL error, ensure `LOCAL_HTTPS=true` is set and you have run `mkcert -install`. You may need to visit `https://localhost:8283` directly once and click "Advanced" -> "Proceed to localhost" to bypass the initial browser warning.

### 3. Create Your First Agent

1. Click **"Create Agent"** or **"New Agent"**
2. Select **Ollama** models:
   - **LLM Model**: `ollama/llama3.1:latest` (or your chosen model)
   - **Embedding Model**: `ollama/nomic-embed-text`
3. Click **Create**
4. Start chatting with your agent!

### 4. Run Tests (Optional)

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_server.py -v

# Run with coverage
uv run pytest --cov=letta tests/
```

---

## Troubleshooting

### Windows-Specific Issues

**Issue: ADE cannot connect to localhost (SSL Error)**
```bash
# 1. Verify certificates exist in certs/ directory
ls certs/localhost.pem certs/localhost-key.pem

# 2. Re-run mkcert installation
mkcert -install

# 3. Ensure LOCAL_HTTPS=true is set in your environment
# 4. Visit https://localhost:8283 directly in your browser and accept the risk
```

**Issue: "psql: command not found"**
```powershell
# Add PostgreSQL to PATH
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
# Make it permanent via System Environment Variables
```

**Issue: "Permission denied" when installing uv**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue: Ollama not starting**
```powershell
# Check if Ollama service is running
Get-Process ollama

# Restart Ollama
Stop-Process -Name ollama -Force
ollama serve
```

**Issue: PostgreSQL service not starting**
```powershell
# Check service status
Get-Service postgresql*

# Start service manually
Start-Service postgresql-x64-16
```

### macOS-Specific Issues

**Issue: "pg_config: command not found"**
```bash
# Add PostgreSQL to PATH
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
# Add to ~/.zshrc for persistence
```

**Issue: "Permission denied: psql"**
```bash
# Fix PostgreSQL permissions
sudo chown -R $(whoami) /opt/homebrew/var/postgresql@16
```

**Issue: Ollama models slow on Intel Macs**
```bash
# Use smaller models for Intel Macs
ollama pull llama3.2:latest  # Faster but less capable
```

### Common Issues (Both Platforms)

**Issue: "ModuleNotFoundError: No module named 'letta'"**
```bash
# Reinstall in editable mode
uv pip install -e .
```

**Issue: Database connection failures**
```bash
# Test PostgreSQL connection
# Windows:
psql -U letta -d letta -h localhost -p 5432
# macOS:
psql -U letta -d letta -h localhost

# Check LETTA_PG_URI format
echo $LETTA_PG_URI  # macOS/Linux
echo $env:LETTA_PG_URI  # Windows PowerShell
```

**Issue: Ollama models not showing in Letta**
```bash
# Verify Ollama is accessible
curl http://localhost:11434/api/tags

# Check Ollama logs
# Windows: Check Event Viewer or Ollama console
# macOS: brew services log ollama

# Restart Letta server
uv run letta server
```

**Issue: Context window errors with local models**
```bash
# Set appropriate context window for your model
# llama3.1: 8192 tokens
# llama3.2: 128000 tokens (1B/3B models)
# Ensure you're not setting context_window higher than model supports
```

---

## Development Workflow

### Quick Start Commands

**Start Development Server:**
```bash
# Windows (PowerShell)
$env:LETTA_PG_URI = "postgresql://letta:letta@localhost:5432/letta"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
uv run letta server

# macOS
export LETTA_PG_URI="postgresql://letta:letta@localhost:5432/letta"
export OLLAMA_BASE_URL="http://localhost:11434"
uv run letta server
```

**Make Changes:**
```bash
# Create a feature branch
git checkout -b feature/your-feature

# Make your changes...

# Format code
uv run black . -l 140

# Run tests
uv run pytest tests/

# Commit
git add .
git commit -m "feat: your feature description"
```

### Useful Commands

```bash
# Check Letta version
uv run letta version

# List agents
uv run letta list agents

# Check database migration status
uv run alembic current

# Create new migration (after model changes)
uv run alembic revision --autogenerate -m "Your migration message"

# Apply migrations
uv run alembic upgrade head
```

---

## Next Steps

✅ **Setup complete!** You're now ready to:

1. **Explore the codebase**: See `EXPLORATION_GUIDE.md` for a detailed walkthrough
2. **Learn the architecture**: Check `ARCHITECTURE.md` for system design
3. **Start contributing**: Review `CONTRIBUTING.md` for contribution guidelines
4. **Use Letta locally**: See `USE.md` for usage patterns

### Recommended First Steps

1. Create an agent with Ollama models via the web UI
2. Test memory persistence by having a conversation
3. Explore the codebase structure (see `EXPLORATION_GUIDE.md`)
4. Join the Discord community: https://discord.gg/letta
5. Browse open issues: https://github.com/letta-ai/letta/issues

---

## Additional Resources

- **Main Repository**: https://github.com/letta-ai/letta
- **Documentation**: https://docs.letta.com
- **Discord**: https://discord.gg/letta
- **Forum**: https://forum.letta.com
- **Ollama Models**: https://ollama.com/library
- **Ollama Documentation**: https://github.com/ollama/ollama/blob/main/docs/api.md
