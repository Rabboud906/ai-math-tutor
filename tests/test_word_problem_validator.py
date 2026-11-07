import json

from word_problem_validator import validate_ai_problem


def test_valid_problem():
    response = json.dumps({
        "question": "Solve this exponential word problem.",
        "topic": "exponential"
    })

    assert validate_ai_problem(response) is True


def test_missing_question():
    response = json.dumps({
        "topic": "linear"
    })

    assert validate_ai_problem(response) is False


def test_invalid_topic():
    response = json.dumps({
        "question": "Find x.",
        "topic": "unknown"
    })

    assert validate_ai_problem(response) is False


def test_invalid_json():
    assert validate_ai_problem("not JSON") is False


def test_ai_cannot_create():
    assert validate_ai_problem("CANNOT_CREATE") is False