import json

try:  # openai 3 ships its HTTP client as httpx2
    import httpx2 as httpx
except ImportError:
    import httpx
import pytest


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("TOKEDY_API_KEY", "TOKEDY_BASE_URL", "TOKEDY_MODEL"):
        monkeypatch.delenv(name, raising=False)


def completion(content):
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "created": 0,
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }


def sse(parts):
    """A streamed chat completion that sends `parts` one chunk at a time."""
    events = []
    for part in parts:
        chunk = {
            "id": "chatcmpl-1",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "test-model",
            "choices": [{"index": 0, "delta": {"content": part}, "finish_reason": None}],
        }
        events.append(f"data: {json.dumps(chunk)}\n\n")
    events.append("data: [DONE]\n\n")
    return "".join(events).encode()


class Recorder:
    """An httpx transport handler that records requests and answers like the API."""

    def __init__(self, parts=("Hel", "lo")):
        self.parts = parts
        self.requests = []

    def __call__(self, request):
        self.requests.append(request)
        body = json.loads(request.content)
        if body.get("stream"):
            return httpx.Response(
                200, content=sse(self.parts), headers={"content-type": "text/event-stream"}
            )
        return httpx.Response(200, json=completion("".join(self.parts)))
