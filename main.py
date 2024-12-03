import re
import statistics
from pathlib import Path

import llm
import prompts


# TODO: increase this number once the live run works
NUM_RUNS = 1

# Create constants for directory structure
ROOT_DIR = Path(__file__).parent
RESULTS_DIR = ROOT_DIR / "results"

# File constants now include the results directory
PRE_PROMPTS_FILE = RESULTS_DIR / "pre_prompts_by_id.txt"
POST_PROMPTS_FILE = RESULTS_DIR / "post_prompts_by_id.txt"
TEST_PROMPTS_FILE = RESULTS_DIR / "test_prompts_by_id.txt"
RESPONSES_FILE = RESULTS_DIR / "responses.txt"
GRADES_FILE = RESULTS_DIR / "grades.txt"
GRADE_COMPONENTS_FILE = RESULTS_DIR / "grade_components.txt"
STATISTICS_FILE = RESULTS_DIR / "statistics.txt"


def main() -> None:
    _gather_data()
    _process_data()


# TODO: make sure users don't appear to be getting the system prompts info in their responses (this is a problem)
# TODO: We have too many grade not parsed for me to be able to manually go through and check them. That prompt needs to be improved. Post prompting it might help.
def _ensure_results_dir() -> None:
    """Create results directory if it doesn't exist"""
    RESULTS_DIR.mkdir(exist_ok=True)


def _gather_data() -> None:
    # llm.set_live_run_mode()

    # Ensure results directory exists
    _ensure_results_dir()

    run_id = 0

    pre_prompts = prompts.pre()
    post_prompts = prompts.post()
    test_prompts = prompts.test()
    grade_pre_prompt = prompts.grade()

    # Write out all prompts with their indices
    with open(PRE_PROMPTS_FILE, "w") as f:
        for i, prompt in enumerate(pre_prompts):
            f.write(f"{i}: {prompt}\n\n")

    with open(POST_PROMPTS_FILE, "w") as f:
        for i, prompt in enumerate(post_prompts):
            f.write(f"{i}: {prompt}\n\n")

    with open(TEST_PROMPTS_FILE, "w") as f:
        for i, prompt in enumerate(test_prompts):
            f.write(f"{i}: {prompt}\n\n")

    # Create/open files in append mode
    with open(RESPONSES_FILE, "a") as resp_file, open(
        GRADES_FILE, "a"
    ) as grade_file, open(GRADE_COMPONENTS_FILE, "a") as components_file:
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
                            test_prompt, response, grade_pre_prompt
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
    with open(GRADE_COMPONENTS_FILE, "r") as components_file:
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
    with open(RESPONSES_FILE, "r") as resp_file:
        for line in resp_file:
            # TODO: we should do it by response ID here, because the response spans many lines
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

        # Check for invalid grades and get user input for corrections
        corrected_grades = []
        for grade_set, response in zip(grades, responses):
            grade_corrections = []
            for i, grade in enumerate(grade_set):
                if not (1 <= grade <= 10):
                    print(f"\nInvalid grade ({grade}) found for combination {key}")
                    print(f"Component {i + 1} for response:\n{response}")
                    while True:
                        try:
                            new_grade = float(
                                input(
                                    f"Please enter a valid grade (1-10) for component {i + 1}: "
                                )
                            )
                            if 1 <= new_grade <= 10:
                                grade_corrections.append(new_grade)
                                break
                            print("Grade must be between 1 and 10")
                        except ValueError:
                            print("Please enter a valid number")
                else:
                    grade_corrections.append(grade)
            corrected_grades.append(grade_corrections)

        # Use corrected grades for statistics
        num_combos = len(corrected_grades)
        min_grades = [min(g[i] for g in corrected_grades) for i in range(5)]
        max_grades = [max(g[i] for g in corrected_grades) for i in range(5)]
        avg_grades = [statistics.mean(g[i] for g in corrected_grades) for i in range(5)]
        stddev_grades = [
            (
                statistics.stdev(g[i] for g in corrected_grades)
                if len(corrected_grades) > 1
                else -1
            )
            for i in range(5)
        ]

        # For the 5th component, use corrected grades and track response indices
        fifth_component_responses = [(g[4], i) for i, g in enumerate(corrected_grades)]
        min_response_val, min_response_idx = min(
            fifth_component_responses, key=lambda x: x[0]
        )
        max_response_val, max_response_idx = max(
            fifth_component_responses, key=lambda x: x[0]
        )
        avg_response_val = statistics.mean(g[0] for g in fifth_component_responses)

        # Write statistics with response indices
        with open(STATISTICS_FILE, "a") as stats_file:
            stats_file.write(f"Combination {key}:\n")
            stats_file.write(f"  Number of combos: {num_combos}\n")
            stats_file.write(f"  Min grades: {min_grades}\n")
            stats_file.write(f"  Max grades: {max_grades}\n")
            stats_file.write(f"  Average grades: {avg_grades}\n")
            stats_file.write(f"  Stddev grades: {stddev_grades}\n")
            stats_file.write(
                f"  Min response (grade={min_response_val}, response #{min_response_idx}): {responses[min_response_idx]}\n"
            )
            stats_file.write(
                f"  Max response (grade={max_response_val}, response #{max_response_idx}): {responses[max_response_idx]}\n"
            )
            stats_file.write(f"  Average response grade: {avg_response_val}\n")
            stats_file.write("\n")


if __name__ == "__main__":
    main()
