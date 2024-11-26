from anthropic import Anthropic
from dotenv import load_dotenv
import os
from typing import Optional


load_dotenv()  # Load environment variables from .env file


def run(prompt: str) -> str:
    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Call the API with the prompt
    message = client.messages.create(
        model="claude-3-haiku-20240307",  # One of their newest and best models
        max_tokens=1024,  # Adjust based on your needs
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
