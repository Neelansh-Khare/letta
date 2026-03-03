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
