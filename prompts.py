from pathlib import Path

import llm


PROMPTS_DIR = Path(__file__).parent / "prompts"


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
    return _read_prompts("test_prompts.txt")


def pre() -> list[str]:
    prompts = _read_prompt("pre_prompts.txt")
    prompts.append(_generate_prompt("pre_prompt_generation.txt"))
    return prompts


def post() -> list[str]:
    prompts = _read_prompt("post_prompts.txt")
    prompts.append(_generate_prompt("post_prompt_generation.txt"))
    return prompts


def grade() -> str:
    return _read_prompt("grade_prompt.txt")
