# Tokedy Python SDK

Official Python library and command-line tool for Tokedy AI compute.

[Tokedy™](https://tokedy.ai) serves language models through an OpenAI-compatible API. This package is a thin layer over the official [`openai`](https://pypi.org/project/openai/) library: it points the client at Tokedy, reads your Tokedy API key, and adds the `tokedy` command. Everything else works exactly like the OpenAI SDK.

Website: https://tokedy.ai

## Install

```bash
pip install tokedy
```

Python 3.9 or newer.

## Quickstart

```python
from tokedy import Tokedy

client = Tokedy()  # reads TOKEDY_API_KEY
resp = client.chat.completions.create(
    model="<model-id>",
    messages=[{"role": "user", "content": "Hello"}],
)
print(resp.choices[0].message.content)
```

Replace `<model-id>` with a model id from the [models list](https://tokedy.ai/docs).

## Streaming

Pass `stream=True` to get the answer as it is written:

```python
from tokedy import Tokedy

client = Tokedy()
stream = client.chat.completions.create(
    model="<model-id>",
    messages=[{"role": "user", "content": "Write a haiku about tea."}],
    stream=True,
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

## Async

`AsyncTokedy` has the same interface, with `await`:

```python
import asyncio

from tokedy import AsyncTokedy


async def main():
    client = AsyncTokedy()
    resp = await client.chat.completions.create(
        model="<model-id>",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(resp.choices[0].message.content)


asyncio.run(main())
```

Streaming works the same way: pass `stream=True` and iterate with `async for`.

## CLI

Installing the package adds a `tokedy` command.

```bash
# One prompt; the answer streams to stdout
tokedy chat "Say hello" --model <model-id>

# Interactive chat; type exit or press Ctrl+C to quit
tokedy chat --model <model-id>

tokedy --version
```

`--model` falls back to the `TOKEDY_MODEL` environment variable. The CLI prints a one-line banner to stderr, so piping stdout (`tokedy chat "..." > answer.txt`) captures only the answer.

## Configuration

| Environment variable | Used for | Default |
|---|---|---|
| `TOKEDY_API_KEY` | Your API key (`api_key=`) | none, required |
| `TOKEDY_BASE_URL` | API base URL (`base_url=`) | `https://api.tokedy.ai/v1` |
| `TOKEDY_MODEL` | Default model for the `tokedy` CLI | none |

Arguments passed to `Tokedy(...)` win over environment variables. Every other argument (`timeout`, `max_retries`, `default_headers`, `http_client`, …) is passed to the OpenAI client unchanged.

## Getting an API key

Tokedy is available to approved companies. [Request access](https://tokedy.ai/#request), then once approved sign in and create a key under [API keys](https://tokedy.ai/app/keys). The key is shown once; store it as `TOKEDY_API_KEY`:

```bash
export TOKEDY_API_KEY="sk-ty-v1-..."
```

## Support

- Questions: support@tokedy.ai
- Bugs and feature requests: [GitHub issues](https://github.com/tokedy/tokedy-sdk-python/issues)
- Security reports: security@tokedy.ai (see [SECURITY.md](https://github.com/tokedy/tokedy-sdk-python/blob/main/SECURITY.md))

The library sends no telemetry and never logs or prints your API key.

---

TOKEDY™ is a trademark of Tokedy, Inc.
