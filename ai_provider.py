import os
from ollama import chat


def generate_ai_response(prompt):
    """
    Send a prompt to the selected AI provider
    and return its response as text.
    """

    provider = os.getenv("AI_PROVIDER", "ollama")

    if provider == "ollama":
        response = chat(
            model="qwen2.5:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.message.content

    else:
        raise ValueError(
            f"Unsupported AI provider: {provider}"
        )