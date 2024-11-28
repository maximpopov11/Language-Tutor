from anthropic import Anthropic
from dotenv import load_dotenv
import os
import time
from dataclasses import dataclass
from typing import Literal
import random

# Rate limiting constants
REQUEST_LIMIT = 50
TIMEOUT_SECONDS = 60  # 1 minute

# Global request counter
request_count = REQUEST_LIMIT

load_dotenv()  # Load environment variables from .env file


@dataclass
class LLMConfig:
    mode: Literal["live", "test", "dry_run"] = "dry_run"
    test_response: str | None = None
    test_grade_components: tuple[int, int, int, int, int] | None = None


# Global config that can be modified
config = LLMConfig()


def set_test_mode(
    test_response: str | None = None,
    test_grade_components: tuple[int, int, int, int, int] | None = None,
) -> None:
    """Configure test mode with optional fixed responses"""
    config.mode = "test"
    config.test_response = test_response
    config.test_grade_components = test_grade_components


def set_live_run_mode() -> None:
    """Configure live run mode"""
    config.mode = "live"


def _generate_test_response(prompt: str) -> str:
    """Generate a dummy response for testing"""
    if config.test_response is not None:
        return config.test_response

    return f"This is a test response for prompt: {prompt[:50]}..."


def _generate_test_grade() -> tuple[float, float, float, float, float, float]:
    """Generate dummy grade components for testing"""
    if config.test_grade_components is not None:
        components = config.test_grade_components
        # Calculate overall grade as average
        overall = sum(components) / len(components)
        return (overall, *components)

    # Generate random grades between 1 and 10
    components = tuple(random.randint(1, 10) for _ in range(5))
    overall = sum(components) / len(components)
    return (overall, *components)


def run(
    prompt: str,
    preprompt: str | None = None,
    postprompt: str | None = None,
) -> str:
    """Run LLM with support for test and dry run modes"""
    global request_count

    # Check and handle rate limiting
    if request_count <= 0:
        time.sleep(TIMEOUT_SECONDS)
        request_count = REQUEST_LIMIT

    request_count -= 1

    if config.mode == "dry_run":
        print(f"DRY RUN: Would send prompt: {prompt[:100]}...")
        if preprompt:
            print(f"With preprompt: {preprompt[:100]}...")
        if postprompt:
            print(f"With postprompt: {postprompt[:100]}...")
        return "DRY_RUN_RESPONSE"

    if config.mode == "test":
        return _generate_test_response(prompt)

    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    if not preprompt:
        preprompt = ""

    # Call the API with the messages
    response = client.messages.create(
        model="claude-3-haiku-20240307",  # One of their newest and best models
        max_tokens=1024,  # Adjust based on your needs
        system=preprompt,
        messages=[{"role": "user", "content": prompt}],
    )

    if postprompt:
        messages = [
            {"role": "assistant", "content": response.content[0].text},
            {"role": "user", "content": postprompt},
        ]

        response = client.messages.create(
            model="claude-3-haiku-20240307",  # One of their newest and best models
            max_tokens=1024,  # Adjust based on your needs
            system=preprompt,
            messages=messages,
        )

    return response.content[0].text


def grade(
    response: str, grade_prompt: str
) -> tuple[float, float, float, float, float, float]:
    """Grade response with support for test and dry run modes"""
    if config.mode == "dry_run":
        print(f"DRY RUN: Would grade response: {response[:100]}...")
        return ("DRY RUN", 5.0, 5.0, 5.0, 5.0, 5.0)

    if config.mode == "test":
        return _generate_test_grade()

    # Try to parse the last line for grades
    try:
        grade_response = run(response, preprompt=grade_prompt)

        last_line = grade_response.strip().split("\n")[-1]
        grades = [float(grade.strip()) for grade in last_line.split(",")]

        if len(grades) == 5:  # Expect exactly 5 grades
            return response, *grades
    except (ValueError, IndexError):
        # We will manually fix this later
        return response, -1, -1, -1, -1, -1
