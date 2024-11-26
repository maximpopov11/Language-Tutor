from anthropic import Anthropic
from dotenv import load_dotenv
import os


load_dotenv()  # Load environment variables from .env file


def _run(
    prompt: str,
    preprompt: str | None = None,
    postprompt: str | None = None,
) -> str:
    # TODO: use the preprompt and postprompt as system prompts and prompt as the user prompt

    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Call the API with the prompt
    message = client.messages.create(
        model="claude-3-haiku-20240307",  # One of their newest and best models
        max_tokens=1024,  # Adjust based on your needs
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def test(prompt: str, preprompt: str, postprompt: str) -> str:
    return _run(prompt, preprompt=preprompt, postprompt=postprompt)


def grade(prompt: str, preprompt: str) -> str:
    return _run(prompt, preprompt=preprompt)
