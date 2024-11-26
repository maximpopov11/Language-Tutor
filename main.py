import llm
import prompts


# TODO: manage rate limits, probably write to file with intermediate results
def main() -> None:
    for prompt in prompts.get():
        llm.run(prompt)


if __name__ == "__main__":
    main()
