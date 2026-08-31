import json

import pytest

from app.rag.generation.ollama import OllamaLLMProvider

STRUCTURED_RESPONSE = json.dumps(
    {
        "answer": "Grounded answer.",
        "citations": [1],
        "insufficient_evidence": False,
    }
)


class FakeResponse:
    def __init__(
        self,
        response_text: str = STRUCTURED_RESPONSE,
    ) -> None:
        self.response_text = response_text

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(
            {
                "response": self.response_text,
            }
        ).encode()


def test_ollama_provider_generates_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(
        request,
        timeout,
    ) -> FakeResponse:
        return FakeResponse()

    monkeypatch.setattr(
        "app.rag.generation.ollama.urlopen",
        fake_urlopen,
    )

    provider = OllamaLLMProvider(
        model="test-model",
    )

    answer = provider.generate(
        "Test prompt",
    )

    assert answer == STRUCTURED_RESPONSE


def test_qwen_thinking_block_is_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(
        request,
        timeout,
    ) -> FakeResponse:
        return FakeResponse(
            
                "<think>\n"
                "Internal reasoning.\n"
                "</think>\n"
                f"{STRUCTURED_RESPONSE}"
            
        )

    monkeypatch.setattr(
        "app.rag.generation.ollama.urlopen",
        fake_urlopen,
    )

    provider = OllamaLLMProvider(
        model="qwen3:4b",
    )

    answer = provider.generate(
        "Reply exactly.",
    )

    assert answer == STRUCTURED_RESPONSE


def test_empty_prompt_is_rejected() -> None:
    provider = OllamaLLMProvider(
        model="test-model",
    )

    with pytest.raises(
        ValueError,
        match="prompt cannot be empty",
    ):
        provider.generate("   ")


def test_empty_model_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="model cannot be empty",
    ):
        OllamaLLMProvider(
            model="   ",
        )


def test_invalid_timeout_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="timeout must be greater than 0",
    ):
        OllamaLLMProvider(
            model="test-model",
            timeout=0,
        )


def test_connection_error_is_wrapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from urllib.error import URLError

    def broken_urlopen(
        request,
        timeout,
    ):
        raise URLError("offline")

    monkeypatch.setattr(
        "app.rag.generation.ollama.urlopen",
        broken_urlopen,
    )

    provider = OllamaLLMProvider(
        model="test-model",
    )

    with pytest.raises(
        ConnectionError,
        match="Could not connect to Ollama",
    ):
        provider.generate(
            "Test prompt",
        )