import pytest
import ai_provider
from types import SimpleNamespace


def test_ollama_provider(monkeypatch):
    # Create a fake Ollama response
    def fake_chat(model, messages):
        return SimpleNamespace(
            message=SimpleNamespace(
                content="Hello from Ollama!"
            )
        )

    # Replace the real Ollama function
    monkeypatch.setattr(ai_provider, "chat", fake_chat)

    # Select Ollama
    monkeypatch.setenv("AI_PROVIDER", "ollama")

    # Call our actual provider function
    result = ai_provider.generate_ai_response("Say hello")

    assert result == "Hello from Ollama!"


def test_invalid_provider(monkeypatch):
    # Select a provider we don't support
    monkeypatch.setenv("AI_PROVIDER", "invalid")

    # Verify our program rejects it
    with pytest.raises(ValueError):
        ai_provider.generate_ai_response("Hello")