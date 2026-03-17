from typing import List, Dict, Any, Optional
from letta_client import Letta
from letta_client.types import MessageCreateParam

class BenchmarkRunner:
    def __init__(self, client: Letta, agent_id: str):
        self.client = client
        self.agent_id = agent_id
        self.history = []

    def run_interaction(self, message: str) -> List[Any]:
        """Runs a single interaction with the agent."""
        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[MessageCreateParam(role="user", content=message)]
        )
        
        # Store interaction in history
        self.history.append({
            "prompt": message,
            "response": response.messages
        })
        
        return response.messages

    def run_sequence(self, messages: List[str]) -> List[List[Any]]:
        """Runs a sequence of interactions."""
        results = []
        for msg in messages:
            results.append(self.run_interaction(msg))
        return results

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the interaction history."""
        return self.history

    def reset_history(self):
        """Resets the runner's history."""
        self.history = []

    def bulk_add_messages(self, messages: List[Dict[str, str]], model: str):
        """Adds multiple messages to the agent's history without triggering an agent run.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: The model to associate with assistant messages
        """
        # We use the capture endpoint to persist messages without execution
        # The capture endpoint expects a pair of (user messages, assistant response)
        # We group them to minimize requests
        
        total = len(messages)
        print(f"Bulk adding {total} messages...")
        i = 0
        batch_count = 0
        while i < len(messages):
            user_msgs = []
            assistant_msg = {"content": "..."} # Default if no assistant message found
            
            # Collect consecutive user messages
            while i < len(messages) and messages[i]["role"] == "user":
                user_msgs.append({"role": "user", "content": messages[i]["content"]})
                i += 1
            
            # Find the following assistant message
            if i < len(messages) and messages[i]["role"] == "assistant":
                assistant_msg = {"content": messages[i]["content"]}
                i += 1
            
            if user_msgs:
                batch_count += 1
                # print(f"  Sending batch {batch_count} (processed {i}/{total})...")
                # Call the capture endpoint
                payload = {
                    "provider": "ollama", # Hardcoded for now as it's for local benchmark
                    "model": model,
                    "request_messages": user_msgs,
                    "response_dict": assistant_msg
                }
                self.client.post(
                    f"/v1/agents/{self.agent_id}/messages/capture",
                    body=payload,
                    cast_to=Dict[str, Any]
                )
        print(f"Finished bulk adding {total} messages in {batch_count} batches.")
