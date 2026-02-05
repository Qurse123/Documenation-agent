from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def chat(message: str, model: str = "gpt-3.5-turbo") -> str:
    """Send a message to OpenAI and get a response."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content
