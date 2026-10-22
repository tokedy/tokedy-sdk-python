"""The `tokedy` command."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

import openai

from . import __version__
from ._client import Tokedy

BANNER = f"Tokedy™ CLI v{__version__} · https://tokedy.ai"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tokedy", description="Command-line tool for the Tokedy API."
    )
    parser.add_argument("--version", action="version", version=f"tokedy {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="command")
    chat = commands.add_parser(
        "chat", help="Send a prompt, or start an interactive chat without one."
    )
    chat.add_argument("prompt", nargs="?", help="The prompt. Omit it to chat interactively.")
    chat.add_argument(
        "--model", help="Model id. Defaults to the TOKEDY_MODEL environment variable."
    )
    return parser


def _stream(client: Tokedy, model: str, messages: list) -> str:
    """Print the reply as it arrives and return it."""
    reply = []
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            reply.append(text)
            sys.stdout.write(text)
            sys.stdout.flush()
    sys.stdout.write("\n")
    return "".join(reply)


def _chat(prompt: str | None, model: str) -> None:
    client = Tokedy()
    if prompt is not None:
        _stream(client, model, [{"role": "user", "content": prompt}])
        return
    print("Type a message and press Enter. Type 'exit' or press Ctrl+C to quit.", file=sys.stderr)
    messages: list = []
    while True:
        try:
            line = input("> ")
        except EOFError:
            return
        if line.strip() == "exit":
            return
        if not line.strip():
            continue
        messages.append({"role": "user", "content": line})
        messages.append({"role": "assistant", "content": _stream(client, model, messages)})


def main(argv: Sequence[str] | None = None) -> int:
    print(BANNER, file=sys.stderr)
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "chat":
        parser.print_help(sys.stderr)
        return 2
    model = args.model or os.environ.get("TOKEDY_MODEL")
    if not model:
        parser.error(
            "no model given. Pass --model <id> or set the TOKEDY_MODEL environment variable."
        )
    try:
        _chat(args.prompt, model)
    except KeyboardInterrupt:
        print(file=sys.stderr)
        return 130
    except openai.OpenAIError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
