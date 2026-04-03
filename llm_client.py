import os
import requests

def call_llm(prompt):
    api_key = os.getenv("GROQ_API_KEY")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    data = response.json()

    if "choices" not in data:
        return "LLM ERROR"

    return data["choices"][0]["message"]["content"]
