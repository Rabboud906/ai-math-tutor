"""Validation for trusted math-engine problems and constrained AI story choices.

This module deliberately DOES NOT claim to understand arbitrary English stories.
"""
import json
import math

TOPICS = {
    "linear", "quadratic", "system", "absolute_value",
    "rational", "exponential", "logarithmic",
}
DIFFICULTIES = {"easy", "intermediate", "hard"}
NAMES = {"Alicia", "Alex", "Jordan", "Maya", "Sam"}
SETTINGS = {
    "science_lab": "a science laboratory",
    "weather_station": "a weather station",
    "engineering_workshop": "an engineering workshop",
}


def close(actual, expected):
    return math.isclose(float(actual), float(expected), rel_tol=1e-9, abs_tol=1e-8)


def verify_math(topic, answer, coeffs):
    """Independently recompute a result using coefficients (not AI text).

    This checks the math engine's answer. It is not a proof that English text
    means the same thing, nor a check of arbitrary printed solution steps.
    """
    try:
        if topic == "linear":
            a, b, c = coeffs
            return a != 0 and close(answer, (c - b) / a)

        if topic == "quadratic":
            a, b, c = coeffs
            disc = b*b - 4*a*c
            if a == 0 or disc < 0 or len(answer) != 2:
                return False
            roots = sorted(((-b + math.sqrt(disc)) / (2*a),
                            (-b - math.sqrt(disc)) / (2*a)))
            return all(close(v, r) for v, r in zip(sorted(answer), roots))

        if topic == "system":
            a, b, c, d, e, f = coeffs
            x, y = answer
            return a*e-b*d != 0 and close(a*x+b*y, c) and close(d*x+e*y, f)

        if topic == "absolute_value":
            a, b, c = coeffs
            if a == 0 or c < 0 or len(answer) != 2:
                return False
            roots = sorted(((c-b)/a, (-c-b)/a))
            return all(close(v, r) for v, r in zip(sorted(answer), roots))

        if topic == "rational":
            a, b, c, d, e = coeffs
            if close(c*float(answer)+d, 0):
                return False  # denominator must not be zero
            return close((a*float(answer)+b)/(c*float(answer)+d), e)

        if topic == "exponential":
            if len(coeffs) == 2:
                base, target = coeffs
                slope, offset = 1, 0
            elif len(coeffs) == 3:
                base, target, offset = coeffs
                slope = 1
            else:
                base, target, slope, d = coeffs
                offset = target - d
            return (base > 0 and base != 1 and target > 0 and slope != 0
                    and close(float(answer), (math.log(target, base)-offset)/slope))

        if topic == "logarithmic":
            if len(coeffs) == 2:
                base, exponent = coeffs
                expected = base**exponent
            elif len(coeffs) == 3:
                base, exponent, shift = coeffs
                expected = base**exponent-shift
            else:
                base, multiplier, shift, exponent = coeffs
                if multiplier == 0:
                    return False
                expected = (base**exponent-shift)/multiplier
            return base > 0 and base != 1 and close(answer, expected)

    except (ValueError, TypeError, ZeroDivisionError, OverflowError):
        return False
    return False


def validate_story_choice(raw):
    """AI can choose ONLY an approved person and setting, never math facts."""
    if not isinstance(raw, str) or len(raw) > 1000:
        return None
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict) or set(data) != {"name", "setting"}:
        return None
    if data["name"] not in NAMES or data["setting"] not in SETTINGS:
        return None
    return data


def build_linear_story(coeffs, choice):
    """Trusted template: these WORDS encode a*x + b = c, even for x < 0."""
    a, b, c = coeffs
    return (
        f"At {SETTINGS[choice['setting']]}, {choice['name']} calibrates an instrument. "
        f"Its starting reading is {b} units. Every one-unit change in a signed "
        f"adjustment x changes the reading by {a} units. After the adjustment, "
        f"the reading is {c} units. What is the signed adjustment x? "
        f"(A negative adjustment is allowed.)"
    )


def validate_ai_problem(ai_response):
    """Legacy structure check retained for your earlier five pytest tests.

    WARNING: True only means valid structure, NOT verified story mathematics.
    """
    if not isinstance(ai_response, str) or not ai_response.strip():
        return False
    try:
        data = json.loads(ai_response)
    except (json.JSONDecodeError, ValueError):
        return False
    return (
        isinstance(data, dict)
        and isinstance(data.get("question"), str)
        and bool(data["question"].strip())
        and isinstance(data.get("topic"), str)
        and data["topic"] in TOPICS
    )
