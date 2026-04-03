from tests.benchmarks.common.runner import BenchmarkRunner


class FakeAgentsMessages:
    def __init__(self):
        self.calls = []

    def create(self, agent_id, messages):
        self.calls.append({"agent_id": agent_id, "messages": messages})
        return type("Response", (), {"messages": []})()


class FakeAgents:
    def __init__(self):
        self.messages = FakeAgentsMessages()


class FakeClient:
    def __init__(self):
        self.agents = FakeAgents()
        self.posts = []

    def post(self, path, body, cast_to):
        self.posts.append({"path": path, "body": body, "cast_to": cast_to})
        return "ok"


def test_bulk_add_messages_uses_provider_from_model_handle():
    client = FakeClient()
    runner = BenchmarkRunner(client, "agent-123", "ollama/llama3.1:latest")

    runner.bulk_add_messages(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": "how are you"},
        ]
    )

    assert len(client.posts) == 2
    assert client.posts[0]["body"]["provider"] == "ollama"
    assert client.posts[0]["body"]["model"] == "llama3.1:latest"
    assert client.posts[0]["body"]["request_messages"] == [{"role": "user", "content": "hello"}]
    assert client.posts[0]["body"]["response_dict"] == {"content": "hi"}
    assert client.posts[1]["body"]["response_dict"] == {"content": "..."}
