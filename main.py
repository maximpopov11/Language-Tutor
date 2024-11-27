import llm
import prompts


# TODO: once everything is working, make this bigger at some reasonable number depending on rate limits
NUM_RUNS = 1


def main() -> None:
    _gather_data()
    _process_data()


# TODO: make sure users don't appear to be getting the system prompts info in their responses
def _gather_data() -> None:
    grade_pre_prompt = prompts.grade()

    for pre_prompt in prompts.pre():
        for post_prompt in prompts.post():
            for test_prompt in prompts.test():
                for i in NUM_RUNS:
                    # TODO: save results to a file (protect against accidental rerun and overwrite)
                    # TODO: manage rate limits
                    response = llm.run(
                        test_prompt, postprompt=pre_prompt, post_prompt=post_prompt
                    )
                    grade = llm.grade(response, grade_pre_prompt)


def _process_data() -> None:
    pass
    # TODO: implement


if __name__ == "__main__":
    main()
