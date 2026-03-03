# Issue #3096: Chat Auto-scroll Behavior Fix

## Problem Description
In the agent chat (ADE), the window unconditionally auto-scrolls to the bottom on every new token during streaming. This prevents users from reading earlier messages while a response is being generated.

## Diagnosis
The issue stems from an unconditional update to `scrollTop` in the chat container's message streaming handler. The `.agent-messenger-scroll` container gets forced to the bottom regardless of the user's current scroll position.

## Solution Overview
We need to modify the scroll logic to only auto-scroll if the user is currently at or near the bottom of the chat window.

## Development Steps

### 1. Locate the Frontend Codebase
The frontend source code (React/TypeScript) for the ADE is **not** contained in this repository (`letta`), which primarily hosts the Python backend and pre-built static assets.

**Action:** You need to locate and checkout the separate frontend repository (likely named `letta-ade`, `letta-frontend`, or similar).

### 2. Locate the Relevant Component
Search the frontend codebase for the component handling the chat message list. 
Key search terms:
- `scrollTop`
- `scrollHeight`
- `.agent-messenger-scroll` (class name)
- Events or hooks that trigger on incoming message chunks.

### 3. Implement the Fix
Modify the scroll logic to conditionally update `scrollTop`.

**Code Change:**
Refactor the logic that handles new token updates to include a check for the current scroll position.

```javascript
// Example implementation in the message stream handler
const container = scrollContainerRef.current; // Assuming a React Ref

if (container) {
  const threshold = 100; // pixels from bottom to consider "at bottom"
  const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
  
  // Only auto-scroll if the user is already near the bottom
  if (distanceFromBottom < threshold) {
    container.scrollTop = container.scrollHeight;
  }
}
```

### 4. Testing Locally
1.  **Start Frontend:** Run the frontend development server (e.g., `npm run dev` or `yarn start`).
2.  **Connect Backend:** Ensure your local Letta backend is running (`letta server`) and the frontend is configured to connect to it (usually via `localhost:8283`).
3.  **Reproduction Test:**
    *   Send a message that triggers a long response (e.g., "Write a long story").
    *   While the agent is streaming the response, scroll up to read previous messages.
    *   **Pass Condition:** The scroll position remains fixed where you scrolled.
    *   **Fail Condition:** The window jumps back to the bottom.
4.  **Resume Test:**
    *   Scroll back to the bottom.
    *   **Pass Condition:** Auto-scrolling resumes for subsequent tokens.

### 5. Deployment

#### Option A: Deploying to Cloud ADE (app.letta.com)
If you have access to the production frontend repository:
1.  Commit the fix to a branch.
2.  Open a Pull Request.
3.  Once merged, the CI/CD pipeline should automatically deploy the new version to `app.letta.com`.

#### Option B: Updating the Bundled Local UI
To update the UI served by `letta server` in this repository:
1.  Run the build command in the frontend repository (e.g., `npm run build`).
2.  Locate the build output directory (usually `dist/` or `build/`).
3.  Copy the contents of the build output to `letta/server/static_files/` in this repository.
    *   Ensure `index.html` and the `assets/` folder are placed correctly.
4.  Commit these updated static files to the `letta` repository.
5.  Re-install the python package locally to verify:
    ```bash
    pip install -e .
    letta server
    ```
6.  Open `http://localhost:8283` (or the configured address) to verify the fix works in the local bundle.
