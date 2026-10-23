import json
from types import SimpleNamespace

import pytest

from azure_openai_examples import client as client_mod
from azure_openai_examples import hello, stream, summarize


class FakeResponses:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.reply


def fake_client(reply):
    return SimpleNamespace(responses=FakeResponses(reply))


@pytest.mark.parametrize("endpoint,expected", [
    ("https://my-res.openai.azure.com", "https://my-res.openai.azure.com/openai/v1/"),
    ("https://my-res.openai.azure.com/", "https://my-res.openai.azure.com/openai/v1/"),
    ("https://my-res.openai.azure.com/openai/v1", "https://my-res.openai.azure.com/openai/v1/"),
    ("my-res", "https://my-res.openai.azure.com/openai/v1/"),
])
def test_base_url_normalisation(endpoint, expected):
    assert client_mod.base_url(endpoint) == expected


def test_api_key_auth_is_used_when_key_present(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my-res.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
    c = client_mod.get_client()
    assert str(c.base_url) == "https://my-res.openai.azure.com/openai/v1/"
    assert client_mod.auth_mode() == "API key"


def test_entra_id_is_the_keyless_default(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    assert client_mod.auth_mode() == "Microsoft Entra ID"


def test_missing_settings_exit_with_hint(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
    with pytest.raises(SystemExit):
        client_mod.get_client()
    with pytest.raises(SystemExit):
        client_mod.deployment()


def test_hello_uses_deployment_as_model():
    c = fake_client(SimpleNamespace(output_text="Hi"))
    assert hello.ask(c, "my-deployment", "hello") == "Hi"
    assert c.responses.calls[0]["model"] == "my-deployment"


def test_stream_joins_deltas():
    events = [SimpleNamespace(type="response.output_text.delta", delta=d) for d in ("a", "b", "c")]
    c = fake_client(iter(events))
    assert stream.stream_reply(c, "dep", "hi", out=lambda *a, **k: None) == "abc"


def test_summarize_requests_json_schema_and_parses_result():
    payload = {"title": "Design", "summary": "Short.", "key_points": ["one", "two"], "open_questions": []}
    c = fake_client(SimpleNamespace(output_text=json.dumps(payload)))
    result = summarize.summarize(c, "dep", "some long document")
    assert result == payload
    fmt = c.responses.calls[0]["text"]["format"]
    assert fmt["type"] == "json_schema" and fmt["strict"] is True
    text = summarize.render(result)
    assert text.startswith("# Design") and "  - two" in text and "Open questions" not in text
