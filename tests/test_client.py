import openai
import pytest
from conftest import Recorder, httpx

from tokedy import AsyncTokedy, Tokedy, __version__


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.parametrize("cls", [Tokedy, AsyncTokedy])
def test_defaults_from_env(monkeypatch, cls):
    monkeypatch.setenv("TOKEDY_API_KEY", "sk-ty-v1-env")
    client = cls()
    assert client.api_key == "sk-ty-v1-env"
    assert str(client.base_url) == "https://api.tokedy.ai/v1/"


@pytest.mark.parametrize("cls", [Tokedy, AsyncTokedy])
def test_base_url_env_override(monkeypatch, cls):
    monkeypatch.setenv("TOKEDY_API_KEY", "sk-ty-v1-env")
    monkeypatch.setenv("TOKEDY_BASE_URL", "http://127.0.0.1:3000/v1")
    assert str(cls().base_url) == "http://127.0.0.1:3000/v1/"


@pytest.mark.parametrize("cls", [Tokedy, AsyncTokedy])
def test_arguments_win_over_env(monkeypatch, cls):
    monkeypatch.setenv("TOKEDY_API_KEY", "sk-ty-v1-env")
    monkeypatch.setenv("TOKEDY_BASE_URL", "http://env.example/v1")
    client = cls(api_key="sk-ty-v1-arg", base_url="http://arg.example/v1")
    assert client.api_key == "sk-ty-v1-arg"
    assert str(client.base_url) == "http://arg.example/v1/"


def test_ignores_openai_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://openai.example/v1")
    with pytest.raises(openai.OpenAIError):
        Tokedy()
    monkeypatch.setenv("TOKEDY_API_KEY", "sk-ty-v1-env")
    assert str(Tokedy().base_url) == "https://api.tokedy.ai/v1/"


@pytest.mark.parametrize("cls", [Tokedy, AsyncTokedy])
def test_missing_key(cls):
    with pytest.raises(openai.OpenAIError) as err:
        cls()
    assert "TOKEDY_API_KEY" in str(err.value)
    assert "https://tokedy.ai/app/keys" in str(err.value)


def test_passes_other_arguments_through(monkeypatch):
    monkeypatch.setenv("TOKEDY_API_KEY", "sk-ty-v1-env")
    client = Tokedy(timeout=12.5, max_retries=7, default_headers={"X-Test": "1"})
    assert client.timeout == 12.5
    assert client.max_retries == 7
    assert client.default_headers["X-Test"] == "1"


def test_chat_completion_request():
    recorder = Recorder()
    client = Tokedy(
        api_key="sk-ty-v1-test",
        http_client=httpx.Client(transport=httpx.MockTransport(recorder)),
    )
    resp = client.chat.completions.create(
        model="test-model", messages=[{"role": "user", "content": "Hello"}]
    )
    assert resp.choices[0].message.content == "Hello"
    request = recorder.requests[0]
    assert str(request.url) == "https://api.tokedy.ai/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer sk-ty-v1-test"


def test_with_options_keeps_tokedy_settings():
    client = Tokedy(api_key="sk-ty-v1-test").with_options(timeout=5)
    assert isinstance(client, Tokedy)
    assert str(client.base_url) == "https://api.tokedy.ai/v1/"


async def test_async_streaming():
    recorder = Recorder(parts=("a", "b", "c"))
    client = AsyncTokedy(
        api_key="sk-ty-v1-test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(recorder)),
    )
    stream = await client.chat.completions.create(
        model="test-model", messages=[{"role": "user", "content": "Hi"}], stream=True
    )
    parts = [chunk.choices[0].delta.content async for chunk in stream]
    assert parts == ["a", "b", "c"]
