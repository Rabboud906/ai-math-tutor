import random
import math
import ast
import re
from fractions import Fraction


def _safe_eval(expr: str) -> float:
    """Safely evaluate a math expression supporting sqrt, √, ln, log, and log_base notation.

    Supported examples:
    - "sqrt(9)", "√9", "3+sqrt(16)"
    - "ln(2)", "log(2)" (natural log)
    - "log(8,2)" or "log_2(8)" which means log base 2 of 8
    - standard arithmetic and ** for powers (caret ^ is converted to **)
    """
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")

    s = expr.strip()
    # common text replacements
    s = s.replace('√', 'sqrt')
    s = s.replace('^', '**')

    # convert log_b(a) -> log(a, b)
    s = re.sub(r'log_([0-9\.]+)\s*\(([^)]+)\)', r'log(\2, \1)', s)
    # map ln(...) to log(...)
    s = re.sub(r'\bln\s*\(', 'log(', s)

    node = ast.parse(s, mode='eval')

    allowed_funcs = {
        'sqrt': math.sqrt,
        'log': lambda x, base=None: math.log(x) if base is None else math.log(x, float(base)),
    }

    allowed_names = {
        'e': math.e,
        'pi': math.pi,
    }

    operators = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Pow: lambda a, b: a ** b,
        ast.USub: lambda a: -a,
        ast.UAdd: lambda a: +a,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in operators:
                return operators[op_type](left, right)
            raise ValueError(f"Operator {op_type} not allowed")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in operators:
                return operators[op_type](operand)
            raise ValueError(f"Unary operator {op_type} not allowed")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                fname = node.func.id
                if fname in allowed_funcs:
                    args = [_eval(a) for a in node.args]
                    return allowed_funcs[fname](*args)
            raise ValueError("Function calls are restricted to sqrt/log")
        if isinstance(node, ast.Name):
            if node.id in allowed_names:
                return allowed_names[node.id]
            raise ValueError(f"Name {node.id} not allowed")
        raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    return float(_eval(node))

# --- Problem generators ---
def generate_linear_problem(difficulty):
    if difficulty == "easy":
        a, b, c = random.randint(1,5), random.randint(0,10), random.randint(0,10)
    elif difficulty == "intermediate":
        a, b, c = random.randint(2,10), random.randint(-20,20), random.randint(-20,20)
    else:
        a, b, c = random.randint(5,20), random.randint(-30,30), random.randint(-30,30)

    question = f"Solve for x: {a}x + {b} = {c} ,answer (Enter as x)"
    answer = (c - b) / a
    hint = f"Subtract the constant term {b}, then divide by the coefficient {a}."
    return question, answer, hint, (a, b, c)

def generate_quadratic_problem(difficulty):
    while True:
        a = random.randint(1,5)
        b = random.randint(-10,10)
        c = random.randint(-10,10)
        d = b*b - 4*a*c
        if d >= 0:
            break

    x1 = (-b + math.sqrt(d)) / (2*a)
    x2 = (-b - math.sqrt(d)) / (2*a)

    question = f"Solve for x: {a}x² + {b}x + {c} = 0 , 'answer Enter as x1,x2'"
    hint = f"Use the quadratic formula: x = [-b ± √(b²-4ac)] / 2a"
    return question, (x1, x2), hint, (a, b, c)

def generate_system_equations(difficulty):
    if difficulty == "easy":
        a1, b1, c1 = random.randint(1,5), random.randint(1,5), random.randint(0,10)
        a2, b2, c2 = random.randint(1,5), random.randint(1,5), random.randint(0,10)
    elif difficulty == "intermediate":
        a1, b1, c1 = random.randint(5,10), random.randint(5,10), random.randint(-10,10)
        a2, b2, c2 = random.randint(5,10), random.randint(5,10), random.randint(-10,10)
    else:
        a1, b1, c1 = random.randint(10,15), random.randint(10,15), random.randint(-20,20)
        a2, b2, c2 = random.randint(10,15), random.randint(10,15), random.randint(-20,20)

    det = a1*b2 - a2*b1
    if det == 0:
        return generate_system_equations(difficulty)

    x = (c1*b2 - c2*b1) / det
    y = (a1*c2 - a2*c1) / det
    question = f"Solve the system:\n{a1}x + {b1}y = {c1}\n{a2}x + {b2}y = {c2} , 'answer Enter as x,y'"
    answer = (x, y)
    hint = "Use substitution or elimination method to solve for x and y."
    return question, answer, hint, (a1,b1,c1,a2,b2,c2)

def generate_absolute_value_problem(difficulty):
    if difficulty == "easy":
        a, b, c = random.randint(1,5), random.randint(0,10), random.randint(0,10)
    elif difficulty == "intermediate":
        a, b, c = random.randint(2,10), random.randint(-20,20), random.randint(0,20)
    else:
        a, b, c = random.randint(5,20), random.randint(-30,30), random.randint(0,30)

    question = f"Solve for x: |{a}x + {b}| = {c} , 'answer Enter as x1,x2'"
    if c < 0:
        answer = []
    else:
        sol1 = (c - b) / a
        sol2 = (-c - b) / a
        answer = sorted([sol1, sol2])
    hint = f"Set up two equations: {a}x + {b} = {c} and {a}x + {b} = -{c}."
    return question, answer, hint, (a, b, c)

def generate_rational_problem(difficulty):
    if difficulty == "easy":
        a, b, c, d, e = [random.randint(1,5) for _ in range(5)]
    elif difficulty == "intermediate":
        a, b, c, d, e = [random.randint(5,10) for _ in range(5)]
    else:
        a, b, c, d, e = [random.randint(10,20) for _ in range(5)]

    # Avoid division by zero
    if a - e*c == 0:
        a += 1

    # LaTeX formatted question
    question = (
        r"Solve the rational equation: "
        rf"\(\frac{{{a}x + {b}}}{{{c}x + {d}}} = {e}\) , 'answer Enter as x'"
    )

    answer = (e*d - b) / (a - e*c)
    hint = "Cross-multiply to eliminate the fraction, then solve the resulting linear equation."

    return question, answer, hint, (a, b, c, d, e)

def generate_exponential_problem(difficulty):
    if difficulty == "easy":
        base = random.randint(2,5)
        c = random.randint(1, 100)
        # Correct LaTeX for x in exponent
        question = rf"Solve for $x$: ${base}^{{x}} = {c}$ , 'answer Enter as x'"
        answer = math.log(c, base)
        hint = f"Use logarithms to solve for x: x = log_base({c})"
        return question, answer, hint, (base, c)

    elif difficulty == "intermediate":
        base = random.randint(2,7)
        exponent = random.randint(2,4)
        c = random.randint(1, 100)
        # Correct LaTeX
        question = rf"Solve for $x$: ${base}^{{x + {exponent}}} = {c}$ , 'answer Enter as x'"
        answer = math.log(c, base) - exponent
        hint = f"Use logarithms to solve for x: x = log_base({c}) - {exponent}"
        return question, answer, hint, (base, c, exponent)
    else:
        base = random.randint(3,10)
        exponent = random.randint(3,5)
        c = random.randint(1, 100)
        d = random.randint(10,30)
        # Correct LaTeX
        question = rf"Solve for $x$: ${base}^{{{exponent}x + {c-d}}} = {c}$ , 'answer Enter as x'"
        answer = (math.log(c, base) - (c-d)) / exponent
        hint = f"Use logarithms to solve for x: x = (log_base({c}) - ({c-d})) / {exponent}"
        return question, answer, hint, (base, c, exponent, d)


def generate_logarithmic_problem(difficulty):
    if difficulty == "easy":
        base = random.randint(2,5)
        c = random.randint(1, 5)
        question = rf"Solve for $x$: $\log_{{{base}}}(x) = {c}$ , 'answer Enter as x'"
        answer = base**c
        hint = f"Use the definition of logarithm: x = {base}^{c}"
        return question, answer, hint, (base, c)
    elif difficulty == "intermediate":
        base = random.randint(2,7)
        exponent = random.randint(2,4)
        c = random.randint(2, 5)
        question = rf"Solve for $x$: $\log_{{{base}}}(x + {exponent}) = {c}$ , 'answer Enter as x'"
        answer = (base**c) - exponent
        hint = f"Rearrange to isolate x: x = {base}^({c}) - {exponent}"
        return question, answer, hint, (base, c, exponent)
    else:
        base = random.randint(3,10)
        exponent = random.randint(3,5)
        c = random.randint(1, 10)
        d = random.randint(10,30)
        question = rf"Solve for $x$: $\log_{{{base}}}({c}x + {exponent}) = {d}$ , 'answer Enter as x'"
        answer = (base**d - exponent) / c
        hint = f"Rearrange to isolate x: x = ({base}^{d} - {exponent}) / {c}"
        return question, answer, hint, (base, c, exponent, d)




def generate_problem(problem_type, difficulty):
    if problem_type == "linear":
        return generate_linear_problem(difficulty), "linear"
    elif problem_type == "quadratic":
        return generate_quadratic_problem(difficulty), "quadratic"
    elif problem_type == "system":
        return generate_system_equations(difficulty), "system"
    elif problem_type == "absolute_value":
        return generate_absolute_value_problem(difficulty), "absolute_value"
    elif problem_type == "rational":
        return generate_rational_problem(difficulty), "rational"
    elif problem_type == "exponential":
        return generate_exponential_problem(difficulty), "exponential"
    elif problem_type == "logarithmic":
        return generate_logarithmic_problem(difficulty), "logarithmic"
    elif problem_type == "word_problem":
        # Pick a random type from existing types
        possible_types = [
            "linear", "quadratic", "system", "absolute_value",
            "rational", "exponential", "logarithmic"
        ]
        chosen_type = random.choice(possible_types)
        
        if chosen_type == "linear":
            return generate_linear_problem(difficulty), "word_problem_linear"
        elif chosen_type == "quadratic":
            return generate_quadratic_problem(difficulty), "word_problem_quadratic"
        elif chosen_type == "system":
            return generate_system_equations(difficulty), "word_problem_system"
        elif chosen_type == "absolute_value":
            return generate_absolute_value_problem(difficulty), "word_problem_absolute_value"
        elif chosen_type == "rational":
            return generate_rational_problem(difficulty), "word_problem_rational"
        elif chosen_type == "exponential":
            return generate_exponential_problem(difficulty), "word_problem_exponential"
        elif chosen_type == "logarithmic":
            return generate_logarithmic_problem(difficulty), "word_problem_logarithmic"

# --- Check answers ---
def check_linear(user, correct, tol=0.1):
    try:
        # accept expressions like sqrt(9), √9, ln(2), log_2(8), 3/2, etc.
        user_val = _safe_eval(user)
        return abs(user_val - correct) < tol
    except Exception:
        return False

def check_quadratic(user, correct, tol=0.1):
    try:
        # 1. Clean up input: remove 'x', '=', and convert 'and' to comma
        #    This handles: "x=3, x=5", "3 and 5", "x1=3, x2=5"
        user_clean = user.lower().replace('x', '').replace('=', '').replace('and', ',')
        
        # 2. Split by comma or semicolon
        parts = [p.strip() for p in re.split(r'[,;]', user_clean) if p.strip()]
        
        # 3. Evaluate user numbers
        user_vals = [_safe_eval(p) for p in parts]
        
        if not user_vals:
            return False

        # 4. Compare User Answers vs Correct Answers
        #    Check A: Every number the user typed must be a valid root
        for u in user_vals:
            # Is 'u' close enough to ANY of the correct answers?
            if not any(abs(u - c) < tol for c in correct):
                return False # User typed a wrong number

        #    Check B: Every correct root must be represented in user's answers
        for c in correct:
            # Is 'c' covered by ANY of the user's answers?
            if not any(abs(c - u) < tol for u in user_vals):
                return False # User missed a root

        return True
    except Exception:
        return False

def check_system(user, correct, tol=1e-6):
    try:
        x_str, y_str = [s.strip() for s in user.split(",")]
        x_user = _safe_eval(x_str)
        y_user = _safe_eval(y_str)
        return (abs(x_user - correct[0]) < tol) and (abs(y_user - correct[1]) < tol)
    except ValueError:
        return None
    except Exception:
        return False
def check_absolute_value(user, correct, tol=0.1):
    try:
        parts = [p.strip() for p in re.split(r'[,;]', user) if p.strip()]
        answers = sorted([round(_safe_eval(x), 2) for x in parts])
        return answers == sorted([round(float(c), 2) for c in correct])
    except Exception:
        return False
def check_rational(user, correct, coeffs, tol=0.1):
    a, b, c, d, e = coeffs
    try:
        x = _safe_eval(user)
        if abs(c*x + d) < tol:
            return False
        return abs(x - correct) < tol
    except Exception:
        return False

def check_exponential(user_input, coeffs, tol=0.1):
    try:
        x = _safe_eval(user_input)
        
        # Determine problem type from coeffs
        if len(coeffs) == 2:  # base^x = c
            base, c = coeffs
            return abs(base**x - c) < tol
        
        elif len(coeffs) == 3:  # base^(x+k) = c
            base, c, k = coeffs
            return abs(base**(x + k) - c) < tol
        
        elif len(coeffs) == 4:  # base^(m x + b) = c
            base, c, m, d = coeffs
            return abs(base**(m*x + (c-d)) - c) < tol
        
        return False
    except Exception:
        return False

def check_logarithmic(user_input, coeffs, tol=0.1):
    try:
        x = _safe_eval(user_input)
        
        if len(coeffs) == 2:  # Easy: log_base(x) = k
            base, k = coeffs
            return abs(base**k - x) < tol
        
        elif len(coeffs) == 3:  # Intermediate: log_base(x + shift) = k
            base, c, exponent = coeffs
            return abs((base**c - exponent) - x) < tol
        
        elif len(coeffs) == 4:  # Hard: log_base(m*x + b) = k
            base, c, exponent, d = coeffs
            return abs(((base**d - exponent) / c) - x) < tol
        
        return False
    except Exception:
        return False


# --- Step-by-step helpers ---
def get_linear_steps(coeffs):
    a, b, c = coeffs
    return [
        f"Start with: {a}x + {b} = {c}",
        f"Subtract {b}: {a}x = {c - b}",
        f"Divide by {a}: x = {round((c - b)/a, 2)}"
    ]

def get_quadratic_steps(coeffs):
    a, b, c = coeffs
    d = b*b - 4*a*c
    sqrt_d = math.sqrt(d)
    return [
        f"Start with: {a}x² + {b}x + {c} = 0",
        f"Calculate discriminant: D = {b}² - 4*{a}*{c} = {d}",
        f"Apply quadratic formula: x = [-{b} ± √{d}] / (2*{a})",
        f"Solve for roots: x1 = {round((-b + sqrt_d)/(2*a), 2)}, x2 = {round((-b - sqrt_d)/(2*a), 2)}"
    ]

def get_system_steps(coeffs):
    a1, b1, c1, a2, b2, c2 = coeffs
    det = a1*b2 - a2*b1
    x = (c1*b2 - c2*b1) / det
    y = (a1*c2 - a2*c1) / det
    return [
        f"Start with the system:\n{a1}x + {b1}y = {c1}\n{a2}x + {b2}y = {c2}",
        "Calculate the determinant: D = a1*b2 - a2*b1",
        f"Calculate x: x = (c1*b2 - c2*b1) / D = {round(x, 2)}",
        f"Calculate y: y = (a1*c2 - a2*c1) / D = {round(y, 2)}"
    ]
def get_absolute_value_steps(coeffs):
    a, b, c = coeffs
    return [
        f"Start with: |{a}x + {b}| = {c}",
        f"Set up two equations: {a}x + {b} = {c} and {a}x + {b} = -{c}",
        f"Solve first equation: {a}x = {c - b} => x = {round((c - b)/a, 2)}",
        f"Solve second equation: {a}x = {-c - b} => x = {round((-c - b)/a, 2)}"
    ]
def get_rational_steps(coeffs):
    a, b, c, d, e = coeffs
    return [
        f"Start with: ({a}x + {b}) / ({c}x + {d}) = {e}",
        "Cross-multiply to eliminate the fraction:",
        f"{a}x + {b} = {e}({c}x + {d})",
        f"Simplify and rearrange to form a linear equation:",
        f"{a}x + {b} = {e*c}x + {e*d}",
        f"Bring like terms together: ({a} - {e*c})x = {e*d - b}",
        f"Solve for x: x = ({e*d - b}) / ({a} - {e*c}) = {round((e*d - b)/(a - e*c), 2)}"
    ]
def get_exponential_steps(coeffs):
    if len(coeffs) == 2:
        base, c = coeffs
        return [
            f"Start with: {base}^x = {c}",
            f"Take logarithm of both sides: log({base}^x) = log({c})",
            f"Use log power rule: x * log({base}) = log({c})",
            f"Solve for x: x = log({c}) / log({base}) = {round(math.log(c)/math.log(base), 2)}"
    ]
    elif len(coeffs) == 3:
        base, c, exponent = coeffs
        return [
            f"Start with: {base}^(x + {exponent}) = {c}",
            f"Take logarithm of both sides: log({base}^(x + {exponent})) = log({c})",
            f"Use log power rule: (x + {exponent}) * log({base}) = log({c})",
            f"Solve for x: x = (log({c}) / log({base})) - {exponent} = {round((math.log(c)/math.log(base)) - exponent, 2)}"
    ]
    else:
        base, c, exponent, d = coeffs
        return [
            f"Start with: {base}^({exponent}x + {c-d}) = {c}",
            f"Take logarithm of both sides:",
            f"log({base}^({exponent}x + {c-d})) = log({c})",
            f"Apply power rule:",
            f"({exponent}x + {c-d})·log({base}) = log({c})",
            f"Solve for x:",
            f"x = (log({c})/log({base}) - ({c-d})) / {exponent} = "
            f"{round((math.log(c, base) - (c-d))/exponent, 2)}"
        ]
def get_logarithmic_steps(coeffs):
    if len(coeffs) == 2:
        base, c = coeffs
        return [
            f"Start with: log_base({base})(x) = {c}",
            f"Rewrite in exponential form: {base}^{c} = x",
            f"so x = {round(base**c, 2)}"
    ]
    elif len(coeffs) == 3:
        base, c, exponent = coeffs
        return [
            f"Start with: log_base({base})(x + {exponent}) = {c}",
            f"Rewrite in exponential form: {base}^{c} = x + {exponent}",
            f"Solve for x: x = {base}^{c} - {exponent} = {round(base**c - exponent, 2)}"
        ]
    else:
        base, c, exponent, d = coeffs
        return [
            f"Start with: log_base({base})({c}x + {exponent}) = {d}",
            f"Rewrite in exponential form: {base}^{d} = {c}x + {exponent}",
            f"Solve for x: x = ({base}^{d} - {exponent}) / {c} = {round((base**d - exponent)/c, 2)}"
        ]