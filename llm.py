from anthropic import Anthropic
from dotenv import load_dotenv
import os


load_dotenv()  # Load environment variables from .env file


def run(
    prompt: str,
    preprompt: str | None = None,
    postprompt: str | None = None,
) -> str:
    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Build messages list starting with any system prompts
    messages = []
    if preprompt:
        messages.append({"role": "system", "content": preprompt})
    messages.append({"role": "user", "content": prompt})
    if postprompt:
        messages.append({"role": "system", "content": postprompt})

    # Call the API with the messages
    message = client.messages.create(
        model="claude-3-haiku-20240307",  # One of their newest and best models
        max_tokens=1024,  # Adjust based on your needs
        messages=messages,
    )
    return message.content[0].text


def grade(prompt: str, preprompt: str) -> str:
    response = run(prompt, preprompt=preprompt)
