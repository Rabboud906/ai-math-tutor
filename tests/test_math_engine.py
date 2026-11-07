import pytest

from math_engine import (
    check_linear,
    check_quadratic,
    check_system,
    check_absolute_value,
    check_rational,
    check_exponential,
    check_logarithmic,
)


# Linear equations
def test_linear():
    assert check_linear("2", 2)
    assert not check_linear("5", 2)


# Quadratic equations
def test_quadratic():
    assert check_quadratic("2,3", (2, 3))
    assert check_quadratic("3,2", (2, 3))
    assert not check_quadratic("2,5", (2, 3))


# Systems of equations
def test_system():
    assert check_system("2,3", (2, 3)) is True
    assert check_system("3,2", (2, 3)) is False


# Absolute value
def test_absolute_value():
    assert check_absolute_value("-2,2", [-2, 2])
    assert not check_absolute_value("1,2", [-2, 2])


# Rational equations
def test_rational():
    coeffs = (3, 1, 1, 2, 2)
    assert check_rational("3", 3, coeffs)
    assert not check_rational("-2", 3, coeffs)


# Exponential equations: 2^x = 8
def test_exponential():
    assert check_exponential("3", (2, 8))
    assert not check_exponential("4", (2, 8))


# Logarithmic equations: log_2(x) = 3
def test_logarithmic():
    assert check_logarithmic("8", (2, 3))
    assert not check_logarithmic("4", (2, 3))


# Invalid math input
def test_invalid_input():
    assert not check_linear("abc", 2)
    assert not check_linear(
        "__import__('os').system('echo hello')", 2
    )