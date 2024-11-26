import llm
import prompts


NUM_RUNS = 1


def main() -> None:
    _gather_data()
    _process_data()


def _gather_data() -> None:
    grade_pre_prompt = prompts.grade()

    for pre_prompt in prompts.pre():
        for post_prompt in prompts.post():
            for test_prompt in prompts.test():
                for i in NUM_RUNS:
                    # TODO: save results to a file (protect against accidental rerun and overwrite)
                    # TODO: manage rate limits
                    response = llm.test(test_prompt, pre_prompt, post_prompt)
                    grade = llm.grade(response, grade_pre_prompt)


def _process_data() -> None:
    pass
    # TODO: implement


if __name__ == "__main__":
    main()
