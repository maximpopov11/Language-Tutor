import llm
import prompts


def main() -> None:
    for prompt in prompts.get():
        llm.run(prompt)


if __name__ == "__main__":
    main()
