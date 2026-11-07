import json
from types import SimpleNamespace

import ai_gen


def mock_ai_response(monkeypatch, content):
    """Replace the real Hugging Face client with a fake one."""

    def fake_create(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content)
                )
            ]
        )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fake_create)
        )
    )

    monkeypatch.setattr(ai_gen, "client", fake_client)


def test_ai_generates_valid_question(monkeypatch):
    response = {
        "question": "Solve 2x + 3 = 7",
        "answer": "2",
        "steps": ["Subtract 3", "Divide by 2"]
    }

    mock_ai_response(monkeypatch, json.dumps(response))

    question, answer, steps = ai_gen.get_ai_word_problem(
        "linear", "easy"
    )

    assert question == "Solve 2x + 3 = 7"
    assert answer == "2"
    assert len(steps) == 2


def test_ai_handles_coordinate_answers(monkeypatch):
    response = {
        "question": "Find (x,y). (Enter as x, y)",
        "answer": "(3, 5)",
        "steps": ["Solve the system"]
    }

    mock_ai_response(monkeypatch, json.dumps(response))

    _, answer, _ = ai_gen.get_ai_word_problem(
        "system", "easy"
    )

    assert answer == "(3,5)"


def test_ai_handles_invalid_json(monkeypatch):
    mock_ai_response(monkeypatch, "not valid JSON")

    question, answer, steps = ai_gen.get_ai_word_problem(
        "linear", "easy"
    )

    assert "Error generating problem" in question
    assert steps


def test_ai_handles_api_failure(monkeypatch):
    monkeypatch.setattr(ai_gen, "client", None)

    question, answer, steps = ai_gen.get_ai_word_problem(
        "linear", "easy"
    )

    assert "Error generating problem" in question
    assert steps


from ai_validator import verify_linear_answer


def test_ai_math_verification():
    # AI gives the correct answer
    assert verify_linear_answer("2*x+3=7", "2") is True

    # AI gives an incorrect answer
    assert verify_linear_answer("2*x+3=7", "5") is False