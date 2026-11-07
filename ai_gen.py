import json
import re
import os
from huggingface_hub import InferenceClient

# Read API key from environment
api_key = os.environ.get("HF_API_KEY")
if not api_key:
    # Don't initialize the client when no API key is provided. The calling
    # code will receive a clear error response from get_ai_word_problem.
    print("Warning: HF_API_KEY not found in environment variables. AI word problems will be disabled.")
    client = None
else:
    # The InferenceClient expects the token parameter name 'token'
    # (older code used 'api_key' which will not authenticate properly).
    client = InferenceClient(token=api_key)


def get_ai_word_problem(topic, difficulty):
    prompt = (
        f"Create a {difficulty} math word problem about {topic}. "
        "STRICT JSON RULES:\n"
        "1. Return valid JSON with keys: 'question', 'answer', and 'steps'.\n"
        "2. 'answer': MUST be a pure number, fraction, or coordinate pair ONLY.\n"
        "   - Single value example: '5' or '1/2'\n"
        "   - System/Coordinate example: '(3, 5)'\n"
        "3. If the answer is a coordinate/system, you MUST add '(Enter as x, y)' to the end of the 'question' text.\n"
        "4. 'steps': A list of strings explaining the solution.\n"
        "5. Use '$' for inline math (e.g., $x^2$).\n"
        "   Example: { \"question\": \"Find the intersection... (Enter as x, y)\", \"answer\": \"(2, 4)\", \"steps\": [\"...\"] }"
    )
    
    try:
        if client is None:
            raise RuntimeError("Inference client is not configured. Set HF_API_KEY in your environment to enable AI word problems.")

        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct", 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        # Fix LaTeX escapes
        fixed_content = content.replace(r'\(', '$').replace(r'\)', '$')
        for cmd in [r'frac', r'sqrt', r'times', r'div', r'pm', r'approx', r'cdot']:
            fixed_content = re.sub(r'(?<!\\)\\' + cmd, r'\\\\' + cmd, fixed_content)

        data = json.loads(fixed_content)
        
        # --- ANSWER CLEANING LOGIC ---
        raw_answer = str(data.get('answer', '0')).strip()
        
        # 1. Check for Coordinate Pattern: (num, num)
        # Matches: (3, 4), (-1.5, 2/3), ( 5 , 6 )
        coord_match = re.search(r'\(\s*[-+]?\d*\.?\d+(?:/\d+)?\s*,\s*[-+]?\d*\.?\d+(?:/\d+)?\s*\)', raw_answer)
        
        if coord_match:
            # Found a coordinate pair, use it exactly
            clean_answer = coord_match.group(0).replace(" ", "") # Remove spaces -> (3,4)
        else:
            # 2. Check for Single Number Pattern
            # Matches: 5, -5, 5.5, 1/2
            num_match = re.search(r'[-+]?\d*\.?\d+(?:/\d+)?', raw_answer)
            if num_match:
                clean_answer = num_match.group(0)
            else:
                # Fallback: just use whatever the AI sent if regex fails
                clean_answer = raw_answer

        question = data.get('question', 'Question missing')
        steps = data.get('steps', ["Step-by-step solution not provided."])
        
        return question, clean_answer, steps

    except Exception as e:
        print(f"AI Gen Error: {e}")
        return (
            "Error generating problem. Please skip to try again.", 
            "0", 
            ["Solution not available due to generation error."]
        )