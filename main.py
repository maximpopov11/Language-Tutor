import re
import statistics

import llm
import prompts


# TODO: consts for file names (in prompts file too)
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
    # Dictionary to store data for each (i, j, k) combination
    data = {}

    # Read the grade components file
    with open("grade_components.txt", "r") as components_file:
        for line in components_file:
            # Extract run_id and (i, j, k) from the line
            match = re.match(r"(\d+): \((\d+),(\d+),(\d+)\): (.+)", line)
            if match:
                run_id, i, j, k, grades_str = match.groups()
                grades = list(map(float, grades_str.split("\t")))

                # Use (i, j, k) as the key
                key = (int(i), int(j), int(k))
                if key not in data:
                    data[key] = {"grades": [], "responses": []}

                data[key]["grades"].append(grades)

    # Read the responses file to get the 5th component's actual response
    with open("responses.txt", "r") as resp_file:
        for line in resp_file:
            match = re.match(r"(\d+): \((\d+),(\d+),(\d+)\): (.+)", line)
            if match:
                run_id, i, j, k, response = match.groups()
                key = (int(i), int(j), int(k))
                if key in data:
                    data[key]["responses"].append(response)

    # Calculate statistics for each (i, j, k) combination
    for key, values in data.items():
        grades = values["grades"]
        responses = values["responses"]

        num_combos = len(grades)
        min_grades = [min(g[i] for g in grades) for i in range(5)]
        max_grades = [max(g[i] for g in grades) for i in range(5)]
        avg_grades = [statistics.mean(g[i] for g in grades) for i in range(5)]
        stddev_grades = [statistics.stdev(g[i] for g in grades) for i in range(5)]

        # For the 5th component, find the actual min, max, and average rated response
        fifth_component_responses = [g[4] for g in grades]
        min_response = min(fifth_component_responses)
        max_response = max(fifth_component_responses)
        avg_response = statistics.mean(fifth_component_responses)

        print(f"Combination {key}:")
        print(f"  Number of combos: {num_combos}")
        print(f"  Min grades: {min_grades}")
        print(f"  Max grades: {max_grades}")
        print(f"  Average grades: {avg_grades}")
        print(f"  Stddev grades: {stddev_grades}")
        print(f"  Min response for 5th component: {min_response}")
        print(f"  Max response for 5th component: {max_response}")
        print(f"  Average response for 5th component: {avg_response}")
    # TODO: implement (check for -1 (manually set) or other illegal grade values)


if __name__ == "__main__":
    main()
