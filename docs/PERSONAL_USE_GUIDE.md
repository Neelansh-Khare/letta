# Letta Personal Use Guide

This guide explains how you can use Letta for your own personal use, highlighting the differences between running a local server and using the production Letta Cloud application.

## Two Ways to Use Letta

There are two primary ways to interact with the Letta platform, each with its own advantages.

### 1. Local Development Server (Your Current Setup)

This is the environment you have just configured. It involves running the Letta server, a database, and local language models (via Ollama) directly on your own machine.

-   **Purpose**: Primarily for development, testing new features, and contributing to the Letta project. It's also great for experimentation with different open-source models in a private environment.
-   **Pros**:
    -   **Total Privacy**: All your data, agents, and conversations stay on your local machine.
    -   **Full Control**: You can modify the source code, experiment with any model Ollama supports, and have complete control over the environment.
    -   **Cost-Free**: Uses your own computer's resources, so there are no service fees (beyond your electricity bill!).
-   **Cons**:
    -   **Requires Maintenance**: You are responsible for starting the server, managing the database, and keeping everything updated.
    -   **Resource Intensive**: Running language models locally can be demanding on your computer's CPU, GPU, and RAM.
    -   **Limited Power**: The performance and capability of your agents are limited by the power of your local hardware and the size of the local models you can run.

### 2. Letta Cloud (Production App)

Letta Cloud is the hosted, managed, and production-ready version of the application, accessible at `https://app.letta.com`.

-   **Purpose**: For general users who want a powerful, reliable, and "always-on" agent platform without the hassle of managing their own infrastructure.
-   **Pros**:
    -   **Zero Setup**: Just sign up and start using it. No databases, servers, or local models to manage.
    -   **Powerful Models**: Access to state-of-the-art, large-scale models (like GPT-4, Claude 3, etc.) that are too large to run on most personal computers.
    -   **Accessibility**: Access your agents from any device with a web browser.
    -   **Managed Service**: All maintenance, updates, and scaling are handled for you.
-   **Cons**:
    -   **Data is Hosted**: Your data is stored securely on Letta's cloud servers, not locally.
    -   **Usage-Based Costs**: There may be costs associated with usage, depending on the subscription tier.

## Getting Started with Letta Cloud for Personal Use

For most personal use cases where you want a reliable and powerful "set it and forget it" solution, using the Letta Cloud app is the recommended path.

### Step 1: Sign Up

Go to `https://app.letta.com` and create an account.

### Step 2: Create Your First Agent

Unlike the local setup where the UI templates might be misconfigured, the UI on the production app is the primary and fully supported way to create agents.
1.  Click **"Create Agent"**.
2.  Choose a template or **"Start from scratch"**.
3.  Select from a wide range of powerful cloud-based models.
4.  Give your agent a system prompt and a name.

### Step 3: Add Your Knowledge

The power of a personal agent comes from the data you give it.
-   **Upload Files**: Go to the "Sources" or "Knowledge" section and upload your documents, notes, PDFs, etc.
-   **Connect Apps**: Connect to other applications to give your agent access to more real-time information (this feature may depend on the current version of the app).

### Step 4: Use Your Agent

Once your agent is created and has access to your knowledge, you can start using it for various tasks:

-   **Personal Knowledge Base**: Ask complex questions about the content of your documents.
    -   *"Summarize the key points from the 'Project Phoenix' PDF I uploaded last week."*
    -   *"What were my main takeaways from the meeting notes dated 2023-10-15?"*
-   **Writing Assistant**: Get help drafting emails, reports, or creative content based on your own data and style.
    -   *"Draft an email to my team summarizing our Q3 performance, using the data from the 'Q3-Report.docx'."*
-   **Task Automation**: Use agents with tools to perform tasks.
    -   *"Search the web for the latest advancements in AI and then write a blog post about it."*

### Advanced Use: The Letta CLI

For power users, the Letta Command Line Interface (CLI) offers a way to manage your agents and resources directly from the terminal. This is especially useful for scripting and automation.

The CLI is run via `uv run letta`.

**Common CLI Commands:**

-   **List all agents**:
    ```bash
    uv run letta list agents
    ```
-   **Check the application version**:
    ```bash
    uv run letta version
    ```
-   **Run database migrations** (for development):
    ```bash
    uv run alembic upgrade head
    ```

The CLI is a powerful tool for developers and advanced users who want to integrate Letta into their scripted workflows.

### Example Use Case: Your Personal Coding Assistant

You can create a specialized agent to help with your programming tasks. This agent can learn from your code, adopt your style, and help you write, debug, and refactor.

**1. Create a "Coding Assistant" Agent**

-   In the Letta UI, create a new agent.
-   Give it a system prompt designed for programming, for example:
    > "You are an expert pair programmer specializing in Python. Your role is to help me write clean, efficient, and well-documented code. When I provide you with code, suggest improvements, identify potential bugs, or help me refactor it. Adhere to the PEP 8 style guide. When I ask for new code, provide it with clear explanations."

**2. Give It Knowledge**

-   Upload your existing projects, code snippets, or entire repositories as knowledge sources.
-   Provide it with technical documentation, API guides, or programming books in PDF format. The agent will use this specific material to answer your questions.

**3. Interact with Your Coding Agent**

Now you can use it as a highly specialized coding partner:

-   **Code Generation**: *"Write a Python function that takes a URL and returns a summary of the page content."*
-   **Refactoring**: *"Here is a function from my project. How can I make it more performant and idiomatic? [paste code]"*
-   **Debugging**: *"I'm getting a `KeyError` in this Python script, but I can't see why. Can you help me find the bug? [paste code]"*
-   **Context-Aware Answers**: *"Based on the 'internal_api_docs.pdf' I uploaded, what parameters does the `create_user` endpoint require?"*

By curating the knowledge you provide, you can create a powerful, personalized coding assistant that understands the context of your specific projects.

## Conclusion

Your **local server setup** is your development sandbox—perfect for coding, testing, and private experimentation.

For a robust, powerful, and hassle-free personal assistant, the **Letta Cloud app** is your go-to solution.
