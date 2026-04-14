from flask import Flask, render_template, request, session
import os
from math_engine import (
    generate_problem,
    check_linear,
    check_quadratic,
    check_system,
    get_linear_steps,
    get_quadratic_steps,
    get_system_steps,
    check_absolute_value, get_absolute_value_steps,
    check_rational, get_rational_steps,
    check_exponential, get_exponential_steps,
    check_logarithmic, get_logarithmic_steps
)
from ai_feedback import explain_mistake
from ai_gen import get_ai_word_problem
import json
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    feedback = None
    hint = None
    steps = None

    # Initialize session defaults
    session.setdefault("score", 0)
    session.setdefault("attempts", 0)
    session.setdefault("problem_type", "linear")
    session.setdefault("difficulty", "easy")
    session.setdefault("word_problem_topic", "linear") # Default sub-topic

    if "question" not in session:
        load_new_problem()

    if request.method == "POST":

        if "exit" in request.form:
            score = session["score"]
            session.clear()
            return render_template("exit.html", score=score)

        if "skip" in request.form:
            load_new_problem()
            feedback = "Skipped! New problem loaded."

        if "difficulty" in request.form or "problem_type" in request.form:
            session["difficulty"] = request.form.get("difficulty", "easy")
            session["problem_type"] = request.form.get("problem_type", "linear")
            # Capture the word problem topic selection
            session["word_problem_topic"] = request.form.get("word_problem_topic", "linear")
            
            load_new_problem()
            feedback = "Settings updated."

        if "answer" in request.form:
            session["attempts"] += 1
            user_answer = request.form["answer"]
            correct_answer = session["answer"]

            # --- CHECKING LOGIC ---
            if session["type"] == "linear":
                correct = check_linear(user_answer, correct_answer)
                if correct:
                    feedback = "Correct! Great work 🎉"
                    session["score"] += 1
                    load_new_problem()
                else:
                    feedback = explain_mistake(session["question"], user_answer, correct_answer)
                    hint = session["hint"]
                    steps = get_linear_steps(session["coeffs"])

            elif session["type"] == "quadratic":
                result = check_quadratic(user_answer, correct_answer)
                if result:
                    feedback = "Correct! Excellent 🎉"
                    session["score"] += 1
                    load_new_problem()
                else:
                    feedback = explain_mistake(session["question"], user_answer, correct_answer)
                    hint = session["hint"]
                    steps = get_quadratic_steps(session["coeffs"])

            elif session["type"] == "system":
                result = check_system(user_answer, correct_answer)
                if result is True:
                    feedback = "Correct! Well done 🎉"
                    session["score"] += 1
                    load_new_problem()
                elif result is False:
                    feedback = explain_mistake(session["question"], user_answer, correct_answer)
                    hint = session["hint"]
                    steps = get_system_steps(session["coeffs"])
                else:
                    feedback = "Invalid input format. Please enter your answer as x,y (e.g., 3/4,-2/5)."

            elif session["type"] == "absolute_value":
                result = check_absolute_value(user_answer, correct_answer)
                if result:
                    feedback = "Correct! Well done 🎉"
                    session["score"] += 1
                    load_new_problem()
                else:
                    feedback = explain_mistake(session["question"], user_answer, correct_answer)
                    hint = session["hint"]
                    steps = get_absolute_value_steps(session["coeffs"])

            elif session["type"] == "rational":
                correct = check_rational(user_answer, correct_answer, session["coeffs"])
                if correct:
                    feedback = "Correct! Great work 🎉"
                    session["score"] += 1
                    load_new_problem()
                else:
                    feedback = explain_mistake(session["question"], user_answer, correct_answer)
                    hint = session["hint"]
                    steps = get_rational_steps(session["coeffs"])

            elif session["type"] == "exponential":
                correct = check_exponential(user_answer, session["coeffs"])
                if correct:
                    feedback = "Correct! Great work 🎉"
                    session["score"] += 1
                    load_new_problem()
                else:
                    feedback = explain_mistake(session["question"], user_answer, correct_answer)
                    hint = session["hint"]
                    steps = get_exponential_steps(session["coeffs"])

            elif session["type"] == "logarithmic":
                correct = check_logarithmic(user_answer, session["coeffs"])
                if correct:
                    feedback = "Correct! Great work 🎉"
                    session["score"] += 1
                    load_new_problem()
                else:
                    feedback = explain_mistake(session["question"], user_answer, correct_answer)
                    hint = session["hint"]
                    steps = get_logarithmic_steps(session["coeffs"])

            elif session["type"] == "word_problem":
                # Clean up the answer for comparison
                clean_correct = str(session["answer"]).lower().strip()
                clean_user = str(user_answer).lower().strip()
                
                is_correct = False
                if clean_user == clean_correct:
                    is_correct = True
                else:
                    # Try fuzzy float comparison
                    try:
                        # Extract first number found if mixed text
                        user_nums = re.findall(r"[-+]?\d*\.\d+|\d+", clean_user)
                        correct_nums = re.findall(r"[-+]?\d*\.\d+|\d+", clean_correct)
                        if user_nums and correct_nums:
                            if abs(float(user_nums[0]) - float(correct_nums[0])) < 0.1:
                                is_correct = True
                    except ValueError:
                        pass

                if is_correct:
                    feedback = "Correct! Great reasoning 🎉"
                    session["score"] += 1
                    load_new_problem()
                else:
                    feedback = explain_mistake(session["question"], user_answer, session["answer"])
                    hint = session["hint"]
                    steps = session.get("custom_steps", ["Solution details unavailable."])

    return render_template(
        "index.html",
        question=session["question"],
        feedback=feedback,
        hint=hint,
        steps=steps,
        score=session["score"],
        problem_type=session["problem_type"],
        difficulty=session["difficulty"],
        word_topic=session.get("word_problem_topic", "linear") 
    )

def load_new_problem():
    if session["problem_type"] == "word_problem":
        # Get the specific topic selected by the user
        user_topic = session.get("word_problem_topic", "linear")
        
        # Map simple keys to better prompt strings for the AI
        topic_map = {
            "linear": "linear equations",
            "quadratic": "quadratic equations",
            "system": "systems of equations",
            "absolute_value": "absolute value equations",
            "rational": "rational equations",
            "exponential": "exponential growth/decay or equations",
            "logarithmic": "logarithmic equations",
            "general": "algebra"
        }
        
        prompt_topic = topic_map.get(user_topic, "algebra")
        
        question, answer, steps = get_ai_word_problem(prompt_topic, session["difficulty"])
        
        print(f"DEBUG: AI Answer is '{answer}' | Topic: {prompt_topic}")
        
        session["question"] = question
        session["answer"] = answer
        session["custom_steps"] = steps 
        session["hint"] = f"This is a {user_topic} word problem. Read carefully and define your variables."
        session["type"] = "word_problem"
        session["coeffs"] = []
    else:
        # Standard logic for non-AI problems
        (question, answer, hint, meta), ptype = generate_problem(
            session["problem_type"],
            session["difficulty"]
        )
        session["question"] = question
        session["answer"] = answer
        session["hint"] = hint
        session["type"] = ptype
        session["coeffs"] = meta
        session["custom_steps"] = None
    
    session["attempts"] = 0

if __name__ == "__main__":
    app.run(debug=True)
