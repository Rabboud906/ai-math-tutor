# AI-Powered Adaptive Math Learning Platform

> An interactive educational web application that generates infinite, adaptive precalculus problems using algorithmic logic and Generative AI.

## 📌 Overview
This project is a full-stack web application designed to help students practice precalculus concepts. Unlike static quiz apps, this platform uses a dual-engine approach:
1.  **Algorithmic Engine:** Generates and verifies algebraic problems (Linear, Quadratic, Systems, etc.) with zero hallucination risk.
2.  **AI Engine (Hugging Face):** leverages Large Language Models (LLMs) to generate unique, context-rich word problems, using strict JSON enforcement to ensure parsable and verifiable answers.

## 🚀 Key Features
* **Dynamic Problem Generation:** Supports Linear, Quadratic, Systems of Equations, Rational, Exponential, Logarithmic, and Absolute Value problems.
* **AI Word Problems:** Integrates the **Hugging Face Inference API** (Qwen-72B) to create unique scenarios for applied math practice.
* **Step-by-Step Solutions:** Provides detailed breakdowns for every problem type to aid student learning.
* **Smart Input Validation:** Uses a custom Abstract Syntax Tree (AST) parser to safely evaluate user mathematical inputs (e.g., `sqrt(5)`, `log(10)`).
* **Interactive UI:** Features gamified feedback, visual success animations, and LaTeX rendering via **MathJax**.
* **Session Management:** Tracks user scores, difficulty levels, and attempts across sessions.

## 🛠️ Technologies Used
* **Backend:** Python 3, Flask
* **AI/ML:** Hugging Face Inference API (LLM Integration)
* **Frontend:** HTML5, CSS3, JavaScript
* **Math Rendering:** MathJax (LaTeX)
* **Deployment:** Render / Gunicorn

## ⚙️ How It Works
### 1. The Math Engine
For standard algebra, the app uses `math_engine.py` to randomize coefficients and calculate solutions algorithmically. This ensures 100% accuracy for core mathematical mechanics.

### 2. The AI Integration
For word problems, the app sends a strictly prompted request to the Hugging Face API, requiring a JSON response containing the question, the numeric answer, and the solution steps. This allows the Python backend to parse and validate the AI's output programmatically.

## 📦 Installation & Local Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-math-tutor.git](https://github.com/YOUR_USERNAME/ai-math-tutor.git)
    cd ai-math-tutor
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**
    Create a `.env` file or export your API key (required for word problems):
    ```bash
    export HF_API_KEY="your_hugging_face_key_here"
    ```

4.  **Run the application**
    ```bash
    python app.py
    ```
    Visit `http://127.0.0.1:5000` in your browser.

## 🛡️ License
This project is licensed under the MIT License - see the LICENSE file for details.
