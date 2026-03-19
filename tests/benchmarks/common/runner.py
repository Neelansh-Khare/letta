from typing import Any, Dict, List

from letta_client import Letta
from letta_client.types import MessageCreateParam

from tests.benchmarks.common.utils import split_model_handle


class BenchmarkRunner:
    def __init__(self, client: Letta, agent_id: str, model_handle: str):
        self.client = client
        self.agent_id = agent_id
        self.history = []
        self.provider_name, self.provider_model = split_model_handle(model_handle)

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

    def run_interaction_timed(self, message: str) -> tuple[List[Any], float]:
        """Runs a single interaction and returns the wall-clock latency."""
        import time

        start = time.perf_counter()
        response = self.run_interaction(message)
        return response, time.perf_counter() - start

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

    def bulk_add_messages(self, messages: List[Dict[str, str]]):
        """Adds multiple messages to the agent's history without triggering an agent run.

        Args:
            messages: List of message dicts with 'role' and 'content'
        """
        total = len(messages)
        i = 0
        while i < len(messages):
            user_msgs = []
            assistant_msg = {"content": "..."}

            while i < len(messages) and messages[i]["role"] == "user":
                user_msgs.append({"role": "user", "content": messages[i]["content"]})
                i += 1

            if i < len(messages) and messages[i]["role"] == "assistant":
                assistant_msg = {"content": messages[i]["content"]}
                i += 1

            if user_msgs:
                payload = {
                    "provider": self.provider_name,
                    "model": self.provider_model,
                    "request_messages": user_msgs,
                    "response_dict": assistant_msg,
                }
                self.client.post(f"/v1/agents/{self.agent_id}/messages/capture", body=payload, cast_to=Dict[str, Any])
        return total

    def ingest_text_entries(self, entries: List[str], batch_size: int = 20) -> int:
        """Adds free-form text entries into the agent history as user-side context."""
        total = 0
        for index in range(0, len(entries), batch_size):
            batch = entries[index : index + batch_size]
            messages = [{"role": "user", "content": entry} for entry in batch]
            total += self.bulk_add_messages(messages)
        return total
