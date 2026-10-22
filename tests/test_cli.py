import builtins

import pytest
from conftest import Recorder, httpx

from tokedy import Tokedy, cli

BANNER = "Tokedy™ CLI v0.1.0 · https://tokedy.ai"


@pytest.fixture
def recorder(monkeypatch):
    """Route the CLI's client through a mock transport; no network."""
    recorder = Recorder()
    monkeypatch.setenv("TOKEDY_API_KEY", "sk-ty-v1-secret")

    def client():
        return Tokedy(http_client=httpx.Client(transport=httpx.MockTransport(recorder)))

    monkeypatch.setattr(cli, "Tokedy", client)
    return recorder


def test_parser_chat_prompt_and_model():
    args = cli.build_parser().parse_args(["chat", "Say hello", "--model", "m1"])
    assert (args.command, args.prompt, args.model) == ("chat", "Say hello", "m1")


def test_parser_chat_without_prompt():
    args = cli.build_parser().parse_args(["chat", "--model", "m1"])
    assert args.prompt is None


def test_version(capsys):
    with pytest.raises(SystemExit) as exit:
        cli.main(["--version"])
    assert exit.value.code == 0
    out, err = capsys.readouterr()
    assert out.strip() == "tokedy 0.1.0"
    assert err.startswith(BANNER)


def test_no_command_shows_help(capsys):
    assert cli.main([]) == 2
    out, err = capsys.readouterr()
    assert out == ""
    assert err.startswith(BANNER)
    assert "chat" in err


def test_missing_model(capsys):
    with pytest.raises(SystemExit) as exit:
        cli.main(["chat", "hi"])
    assert exit.value.code == 2
    _, err = capsys.readouterr()
    assert "TOKEDY_MODEL" in err


def test_missing_key(capsys):
    assert cli.main(["chat", "hi", "--model", "m1"]) == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert "TOKEDY_API_KEY" in err


def test_chat_streams_to_stdout_and_banner_to_stderr(recorder, capsys):
    assert cli.main(["chat", "Say hello", "--model", "m1"]) == 0
    out, err = capsys.readouterr()
    assert out == "Hello\n"
    assert err.strip() == BANNER
    assert "sk-ty-v1-secret" not in out + err
    body = recorder.requests[0].read()
    assert b'"model":"m1"' in body.replace(b" ", b"")
    assert b'"stream":true' in body.replace(b" ", b"")


def test_model_from_env(recorder, monkeypatch, capsys):
    monkeypatch.setenv("TOKEDY_MODEL", "env-model")
    assert cli.main(["chat", "hi"]) == 0
    assert b"env-model" in recorder.requests[0].read()


def test_api_error_is_reported(monkeypatch, capsys):
    monkeypatch.setenv("TOKEDY_API_KEY", "sk-ty-v1-secret")

    def handler(request):
        return httpx.Response(401, json={"error": {"code": 401, "message": "invalid api key"}})

    monkeypatch.setattr(
        cli,
        "Tokedy",
        lambda: Tokedy(
            http_client=httpx.Client(transport=httpx.MockTransport(handler)), max_retries=0
        ),
    )
    assert cli.main(["chat", "hi", "--model", "m1"]) == 1
    _, err = capsys.readouterr()
    assert "invalid api key" in err
    assert "sk-ty-v1-secret" not in err


def test_interactive_keeps_history_until_exit(recorder, monkeypatch, capsys):
    lines = iter(["first", "", "second", "exit"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(lines))
    assert cli.main(["chat", "--model", "m1"]) == 0
    assert len(recorder.requests) == 2
    second = recorder.requests[1].read()
    assert b"first" in second and b"second" in second and b"Hello" in second


def test_interactive_ctrl_c(recorder, monkeypatch, capsys):
    def interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr(builtins, "input", interrupt)
    assert cli.main(["chat", "--model", "m1"]) == 130
