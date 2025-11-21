from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)


def generate_email_from_prompt(prompt: str) -> str:
    """
    Generates an email using OpenAI based on a user-defined prompt.
    Returns plain text email output.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You write clear, professional, polite emails. "
                "You only return the email body without any explanation."
            )
        },
        {
            "role": "user",
            "content": f"Write an email based on these instructions:\n\n{prompt}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
