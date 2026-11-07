"""Safe-first problem pipeline. Does not modify the existing Flask app."""
from math_engine import (
    generate_problem,
    get_linear_steps, get_quadratic_steps, get_system_steps,
    get_absolute_value_steps, get_rational_steps,
    get_exponential_steps, get_logarithmic_steps,
)
from word_problem_validator import (
    TOPICS, DIFFICULTIES, verify_math,
    validate_story_choice, build_linear_story,
)
from ai_provider import generate_ai_response

STEP_FUNCTIONS = {
    "linear": get_linear_steps,
    "quadratic": get_quadratic_steps,
    "system": get_system_steps,
    "absolute_value": get_absolute_value_steps,
    "rational": get_rational_steps,
    "exponential": get_exponential_steps,
    "logarithmic": get_logarithmic_steps,
}

PROMPT = """Choose creative details for a math word problem.
Return ONLY JSON with exactly these keys:
{{"name":"Alex","setting":"science_lab"}}
Allowed names: Alicia, Alex, Jordan, Maya, Sam
Allowed settings: science_lab, weather_station, engineering_workshop
Do not include equations, numbers, explanations, or extra keys.
Choose any combination from the allowed lists.
"""


def generate_safe_problem(topic, difficulty):
    if topic not in TOPICS or difficulty not in DIFFICULTIES:
        raise ValueError("Unsupported topic or difficulty")

    # Regenerate on the rare occasion that math_engine produces invalid math.
    for _ in range(20):
        (question, answer, hint, coeffs), ptype = generate_problem(topic, difficulty)
        if ptype == topic and verify_math(topic, answer, coeffs):
            break
    else:
        raise RuntimeError("Math engine could not generate a valid problem")

    steps = STEP_FUNCTIONS[topic](coeffs)
    result = {
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "answer": answer,
        "hint": hint,
        "coeffs": coeffs,
        "steps": steps,
        "source": "verified_math_fallback",
    }

    # Only linear has an approved narrative template in this first release.
    # Other 6 topics safely show their verified original math question.
    if topic != "linear":
        return result

    try:
        response = generate_ai_response(PROMPT)
        choice = validate_story_choice(response)
        if choice is not None:
            result["question"] = build_linear_story(coeffs, choice)
            result["source"] = "verified_ai_assisted_story"
    except Exception:
        pass  # AI is optional; math still works offline.

    return result


if __name__ == "__main__":
    print("Topics:", ", ".join(sorted(TOPICS)))
    topic = input("Topic: ").strip().lower()
    difficulty = input("Difficulty (easy/intermediate/hard): ").strip().lower()
    result = generate_safe_problem(topic, difficulty)
    print("\nQUESTION:", result["question"])
    print("ANSWER:", result["answer"])
    print("STEPS:")
    for step in result["steps"]:
        print(" -", step)
    print("SOURCE:", result["source"])