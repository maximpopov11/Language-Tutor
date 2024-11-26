from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"


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


def test() -> list[str]:
    return _read_prompts("test_prompts.txt")


def pre() -> list[str]:
    return _read_prompts("pre_prompts.txt")


def post() -> list[str]:
    return _read_prompts("post_prompts.txt")


def grade() -> str:
    with open(PROMPTS_DIR / "grade_prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()
