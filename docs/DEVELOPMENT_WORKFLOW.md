# Letta Development Workflow

This guide outlines the standard workflow for contributing code to the Letta project, from making changes to testing them locally.

## 1. Branching and Making Changes

All new features, bug fixes, or documentation changes should be done in a separate branch.

### Create a New Branch

Start from the `main` branch and create a feature or fix branch. Use a descriptive name that summarizes the change.

```bash
# Make sure you are on the main branch and have the latest changes
git checkout main
git pull origin main

# Create a new branch for your feature
git checkout -b feature/my-new-feature

# Or for a bug fix
git checkout -b fix/bug-in-agent-creation
```

### Make Your Code Changes

Make your desired changes to the codebase. Ensure your code follows the existing style and conventions of the project.

## 2. Formatting and Linting

Before committing your code, it's important to run the project's formatting and linting tools to ensure code quality and consistency. This project uses `ruff` for both linting and formatting.

You can run the checks and formatting from your virtual environment:

```bash
# Check for linting errors
uv run ruff check .

# Automatically fix linting errors (when possible)
uv run ruff check . --fix

# Format your code
uv run ruff format .
```

It's highly recommended to use the pre-commit hooks, which automate this process. (See `setup.md` for installation).

## 3. Committing Your Changes

Once your changes are made and the code is clean, commit them with a clear and descriptive message. This project follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

**Commit Message Format:**

`<type>[optional scope]: <description>`

-   **`feat`**: A new feature
-   **`fix`**: A bug fix
-   **`docs`**: Documentation only changes
-   **`style`**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
-   **`refactor`**: A code change that neither fixes a bug nor adds a feature
-   **`test`**: Adding missing tests or correcting existing tests
-   **`chore`**: Changes to the build process or auxiliary tools and libraries

**Example:**

```bash
git add .
git commit -m "feat(api): add endpoint for creating agents"
```

## 4. Local Testing

Before pushing your changes, you must verify that they work as expected and do not break existing functionality.

### Running Automated Tests

This project uses `pytest`. Run the full test suite to ensure everything is passing.

```bash
# Run all tests
uv run pytest

# Run tests for a specific file
uv run pytest tests/test_server.py
```

### Manual Testing

For changes that impact the server or UI, you should also run the server locally to test your changes manually.

```powershell
# In PowerShell, from the project root

# Set required environment variables
$env:LOCAL_HTTPS = "true"
$env:LETTA_PG_URI = "postgresql://letta:letta@localhost:5432/letta"
$env:OLLAMA_BASE_URL = "http://localhost:11434"

# Start the server
uv run letta server
```

Now you can connect to your local server via the Letta ADE at `https://app.letta.com/development-servers/local/dashboard` and test your changes.

## 5. Submitting for Review

Once your changes are committed and tested, push your branch to the remote repository and open a Pull Request (PR) against the `main` branch.

```bash
# Push your branch to the remote repository
git push origin feature/my-new-feature

# Go to the GitHub repository in your browser and open a Pull Request.
```

Fill out the PR template with details about your changes, why they are needed, and how you tested them. This will help reviewers understand your contribution and provide feedback more effectively.
