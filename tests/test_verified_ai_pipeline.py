import json
import pytest

import verified_ai_pipeline as pipeline
from word_problem_validator import validate_story_choice, verify_math


@pytest.mark.parametrize("topic", sorted(pipeline.STEP_FUNCTIONS))
def test_all_topics_have_verified_math(topic, monkeypatch):
    monkeypatch.setattr(pipeline, "generate_ai_response", lambda _: "CANNOT_CREATE")
    for _ in range(25):
        problem = pipeline.generate_safe_problem(topic, "easy")
        assert problem["topic"] == topic
        assert problem["question"]
        assert problem["steps"]
        assert verify_math(topic, problem["answer"], problem["coeffs"])
        if topic != "linear":
            assert problem["source"] == "verified_math_fallback"


def test_linear_ai_story_keeps_math_and_no_ai_answer(monkeypatch):
    monkeypatch.setattr(
        pipeline, "generate_ai_response",
        lambda prompt: json.dumps({"name": "Maya", "setting": "science_lab"}),
    )
    problem = pipeline.generate_safe_problem("linear", "easy")
    assert problem["source"] == "verified_ai_assisted_story"
    assert "Maya" in problem["question"]
    assert "signed adjustment" in problem["question"]
    assert isinstance(problem["answer"], (int, float))


@pytest.mark.parametrize("bad", [
    "CANNOT_CREATE", "not JSON", "{}",
    '{"name":"Maya","setting":"moon"}',
    '{"name":"Maya","setting":"science_lab","answer":48}',
    '{"name":"Maya","setting":"science_lab","extra_story":"5x+20=250"}',
])
def test_invalid_ai_output_is_rejected(bad, monkeypatch):
    monkeypatch.setattr(pipeline, "generate_ai_response", lambda _: bad)
    result = pipeline.generate_safe_problem("linear", "easy")
    assert result["source"] == "verified_math_fallback"
    assert result["question"].startswith("Solve for x:")


def test_ollama_failure_uses_fallback(monkeypatch):
    def fail(_):
        raise RuntimeError("Ollama offline")
    monkeypatch.setattr(pipeline, "generate_ai_response", fail)
    assert pipeline.generate_safe_problem("linear", "easy")["source"] == "verified_math_fallback"


def test_wrong_ai_answer_does_not_match_equation():
    assert verify_math("linear", 48, (5, 20, 250)) is False
    assert verify_math("linear", 46, (5, 20, 250)) is True


def test_nonreal_rational_answer_is_rejected():
    # (2x+2)/(x+1)=2 is true except at x=-1; invalid generated x=-1.
    assert verify_math("rational", -1, (2, 2, 1, 1, 2)) is False


def test_unsupported_topic_is_rejected():
    with pytest.raises(ValueError):
        pipeline.generate_safe_problem("geometry", "easy")


def test_untrusted_story_fields_are_rejected():
    bad = json.dumps({"name": "Maya 3x+7=22", "setting": "science_lab"})
    assert validate_story_choice(bad) is None


def test_generated_negative_linear_uses_signed_quantity(monkeypatch):
    monkeypatch.setattr(pipeline, "generate_problem",
                        lambda *args: (("Solve for x: 4x + 4 = 0", -1, "hint", (4, 4, 0)), "linear"))
    monkeypatch.setattr(pipeline, "generate_ai_response",
                        lambda _: json.dumps({"name":"Alex","setting":"weather_station"}))
    result = pipeline.generate_safe_problem("linear", "hard")
    assert result["answer"] == -1
    assert "signed adjustment" in result["question"]
    assert result["source"] == "verified_ai_assisted_story"


def test_incorrect_math_engine_result_is_not_served(monkeypatch):
    monkeypatch.setattr(pipeline, "generate_problem",
                        lambda *args: (("wrong", 48, "hint", (5, 20, 250)), "linear"))
    with pytest.raises(RuntimeError, match="could not generate"):
        pipeline.generate_safe_problem("linear", "easy")


def test_legacy_structure_validator_still_works():
    from word_problem_validator import validate_ai_problem
    assert validate_ai_problem('{"question":"Find x", "topic":"linear"}')
    assert not validate_ai_problem('CANNOT_CREATE')
