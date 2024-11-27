from anthropic import Anthropic
from dotenv import load_dotenv
import os


NUM_RETRIES = 3


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


def grade(prompt: str, preprompt: str) -> tuple[str, float, float, float, float, float]:
    # Try up to NUM_RETRIES times to get properly formatted grades
    for attempt in range(NUM_RETRIES):
        response = run(prompt, preprompt=preprompt)

        # Try to parse the last line for grades
        try:
            last_line = response.strip().split("\n")[-1]
            grades = [float(grade.strip()) for grade in last_line.split(",")]

            if len(grades) == 5:  # Expect exactly 5 grades
                return response, *grades
        except (ValueError, IndexError):
            if attempt < 2:  # If not the last attempt
                continue

            # We will manually fix this later
            return response, -1, -1, -1, -1, -1

    return response  # Return the last response if all attempts fail
