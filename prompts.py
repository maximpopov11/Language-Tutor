from pathlib import Path

import llm


PROMPTS_DIR = Path(__file__).parent / "prompts"

# Input prompt file constants
TEST_PROMPTS_FILE = "test_prompts.txt"
PRE_PROMPTS_FILE = "pre_prompts.txt"
PRE_PROMPT_GENERATION_FILE = "pre_prompt_generation.txt"
POST_PROMPTS_FILE = "post_prompts.txt"
POST_PROMPT_GENERATION_FILE = "post_prompt_generation.txt"
GRADE_PROMPT_FILE = "grade_prompt.txt"


def _read_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def _read_prompts(filename: str) -> list[str]:
    """Helper function to read prompts from a file. Handles multi-line prompts separated by blank lines."""
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        content = f.read()
        # Split on double newlines to separate prompts
        prompts = content.strip().split("\n\n")
        # Replace single newlines with spaces within each prompt
        return [
            prompt.replace("\n", " ").strip() for prompt in prompts if prompt.strip()
        ]


def _generate_prompt(filename: str) -> str:
    return llm.run(_read_prompt(filename))


def test() -> list[str]:
    return _read_prompts(TEST_PROMPTS_FILE)


def pre() -> list[str]:
    prompts = _read_prompt(PRE_PROMPTS_FILE)
    prompts.append(_generate_prompt(PRE_PROMPT_GENERATION_FILE))
    return prompts


def post() -> list[str]:
    prompts = _read_prompt(POST_PROMPTS_FILE)
    prompts.append(_generate_prompt(POST_PROMPT_GENERATION_FILE))
    return prompts


def grade() -> str:
    return _read_prompt(GRADE_PROMPT_FILE)
