from sympy import symbols, Eq, solve, sympify

def verify_linear_answer(equation, ai_answer):
    x = symbols("x")

    try:
        # Split the equation into left and right sides
        left, right = equation.split("=")

        # Convert mathematical text into SymPy expressions
        lhs = sympify(left)
        rhs = sympify(right)

        # Solve independently
        solutions = solve(Eq(lhs, rhs), x)

        # Check the AI's answer
        return len(solutions) == 1 and solutions[0] == sympify(ai_answer)

    except Exception:
        return False