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
        self.total_usage = {
            "completion_tokens": 0,
            "prompt_tokens": 0,
            "total_tokens": 0,
            "step_count": 0,
        }
        self.total_latency_seconds = 0.0

    def run_interaction(self, message: str) -> List[Any]:
        """Runs a single interaction with the agent."""
        import time
        start = time.perf_counter()
        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[MessageCreateParam(role="user", content=message)]
        )
        latency = time.perf_counter() - start
        self.total_latency_seconds += latency

        # Update usage
        usage_data = None
        if hasattr(response, "usage") and response.usage:
            usage = response.usage
            self.total_usage["completion_tokens"] += getattr(usage, "completion_tokens", 0)
            self.total_usage["prompt_tokens"] += getattr(usage, "prompt_tokens", 0)
            self.total_usage["total_tokens"] += getattr(usage, "total_tokens", 0)
            self.total_usage["step_count"] += getattr(usage, "step_count", 0)
            usage_data = {
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
                "step_count": getattr(usage, "step_count", 0),
            }

        # Store interaction in history
        memory_calls = []
        for msg in response.messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    name = getattr(tc.function, "name", "") if hasattr(tc, "function") else getattr(tc, "name", "")
                    if any(keyword in name for keyword in ["core_memory", "archival_memory", "recall_memory"]):
                        memory_calls.append({
                            "tool": name,
                            "arguments": getattr(tc.function, "arguments", "") if hasattr(tc, "function") else getattr(tc, "arguments", "")
                        })

        self.history.append({
            "prompt": message,
            "response": response.messages,
            "usage": usage_data,
            "latency_seconds": latency,
            "memory_calls": memory_calls
        })

        return response.messages

    def run_interaction_timed(self, message: str) -> tuple[List[Any], float]:
        """Runs a single interaction and returns the wall-clock latency."""
        # Note: run_interaction now tracks latency internally too, but we keep this for compatibility
        import time
        start = time.perf_counter()
        response_messages = self.run_interaction(message)
        return response_messages, time.perf_counter() - start

    def get_total_usage(self) -> Dict[str, int]:
        """Returns the cumulative usage statistics."""
        return self.total_usage

    def get_total_latency(self) -> float:
        """Returns the cumulative latency."""
        return self.total_latency_seconds

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
