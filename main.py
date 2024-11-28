import llm
import prompts


# TODO: once everything is working, make this bigger at some reasonable number depending on rate limits
NUM_RUNS = 2


def main() -> None:
    _gather_data()
    _process_data()


# TODO: make sure users don't appear to be getting the system prompts info in their responses
# TODO: make sure we don't overwrite file data (num runs 2 should be able to check this)
def _gather_data() -> None:
    run_id = 0

    pre_prompts = prompts.pre()
    post_prompts = prompts.post()
    test_prompts = prompts.test()
    grade_pre_prompt = prompts.grade()

    # Write out all prompts with their indices
    with open("pre_prompts_by_id.txt", "w") as f:
        for i, prompt in enumerate(pre_prompts):
            f.write(f"{i}: {prompt}\n\n")

    with open("post_prompts_by_id.txt", "w") as f:
        for i, prompt in enumerate(post_prompts):
            f.write(f"{i}: {prompt}\n\n")

    with open("test_prompts.txt_by_id", "w") as f:
        for i, prompt in enumerate(test_prompts):
            f.write(f"{i}: {prompt}\n\n")

    # Create/open files in append mode
    with open("responses.txt", "a") as resp_file, open(
        "grades.txt", "a"
    ) as grade_file, open("grade_components.txt", "a") as components_file:
        for i in range(len(pre_prompts)):
            pre_prompt = pre_prompts[i]

            for j in range(len(post_prompts)):
                post_prompt = post_prompts[j]

                for k in range(len(test_prompts)):
                    test_prompt = test_prompts[k]

                    for _ in range(NUM_RUNS):
                        response = llm.run(
                            test_prompt, preprompt=pre_prompt, postprompt=post_prompt
                        )
                        grade, g1, g2, g3, g4, g5 = llm.grade(
                            response, grade_pre_prompt
                        )

                        # Define index once
                        prefix = f"{run_id}: ({i},{j},{k})"

                        # Save results with run_id and strategy indices
                        resp_file.write(f"{prefix}: {response}\n")
                        grade_file.write(f"{prefix}: {grade}\n")
                        components_file.write(
                            f"{prefix}: {g1}\t{g2}\t{g3}\t{g4}\t{g5}\n"
                        )

                        # Flush the files to ensure writing
                        resp_file.flush()
                        grade_file.flush()
                        components_file.flush()

                        run_id += 1


def _process_data() -> None:
    pass
    # TODO: implement (check for -1 (manually set) or other illegal grade values)


if __name__ == "__main__":
    main()
