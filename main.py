import re
import statistics
from pathlib import Path

import llm
import prompts


NUM_RUNS = 90

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
    # _gather_data()
    _process_data()


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
    # Dictionary to store grade and response data by run ID for each (i, j, k) combination
    data = {}

    # Read the grade components file
    with open(GRADE_COMPONENTS_FILE, "r") as components_file:
        for line in components_file:
            # Extract run_id and (i, j, k) from the line
            match = re.match(r"(\d+): \((\d+),(\d+),(\d+)\): (.+)", line)
            if match:
                run_id, i, j, k, grades_str = match.groups()
                grades = list(map(float, grades_str.split("\t")))

                # Use (i, j, k) as the key and run_id as sub-key
                key = (int(i), int(j), int(k))
                run_id = int(run_id)
                if key not in data:
                    data[key] = {}
                if run_id not in data[key]:
                    data[key][run_id] = {"grades": None, "responses": None}

                data[key][run_id]["grades"] = grades

    # Read the responses file to get the 5th component's actual response
    with open(RESPONSES_FILE, "r") as resp_file:
        for line in resp_file:
            match = re.match(r"(\d+): \((\d+),(\d+),(\d+)\): (.+)", line)
            if match:
                run_id, i, j, k, response = match.groups()
                key = (int(i), int(j), int(k))
                run_id = int(run_id)
                if key in data and run_id in data[key]:
                    data[key][run_id]["responses"] = response

    # Calculate statistics for each (i, j, k) combination
    for key, run_id_values in data.items():
        # Track valid and invalid grades
        valid_grades = {}
        valid_responses = {}
        valid_count = 0
        invalid_count = 0

        best_response_id = None
        best_score = -float("inf")
        worst_response_id = None
        worst_score = float("inf")

        for run_id, values in run_id_values.items():
            grades = values["grades"]
            responses = values["responses"]

            for grade_set in grades:
                valid = True
                for grade in grade_set:
                    if grade < 1 or grade > 5:
                        valid = False
                        break

                if valid:
                    score = _get_score_from_grades(grade_set)
                    if score > best_score:
                        best_score = score
                        best_response_id = run_id
                    if score < worst_score:
                        worst_score = score
                        worst_response_id = run_id

                    valid_grades[run_id] = grade_set
                    valid_responses[run_id] = responses
                    valid_count += 1
                else:
                    invalid_count += 1

        total_count = valid_count + invalid_count
        validity_percentage = (
            (valid_count / total_count) * 100 if total_count > 0 else -1
        )

        best_response = valid_responses[best_response_id]
        worst_response = valid_responses[worst_response_id]

        # Calculate statistics using only valid grades
        if valid_count > 0:
            min_grades = [min(g[i] for g in valid_grades) for i in range(5)]
            max_grades = [max(g[i] for g in valid_grades) for i in range(5)]
            avg_grades = [statistics.mean(g[i] for g in valid_grades) for i in range(5)]
            stddev_grades = [
                (
                    statistics.stdev(g[i] for g in valid_grades)
                    if valid_count > 1
                    else -1
                )
                for i in range(5)
            ]

            # Write statistics with validity information
            with open(STATISTICS_FILE, "a") as stats_file:
                stats_file.write(f"Combination {key}:\n")
                stats_file.write(f"  Total components: {total_count}\n")
                stats_file.write(f"  Valid components: {valid_count}\n")
                stats_file.write(f"  Invalid components: {invalid_count}\n")
                stats_file.write(f"  Validity percentage: {validity_percentage:.2f}%\n")
                stats_file.write(f"  Min grades: {min_grades}\n")
                stats_file.write(f"  Max grades: {max_grades}\n")
                stats_file.write(f"  Average grades: {avg_grades}\n")
                stats_file.write(f"  Stddev grades: {stddev_grades}\n")
                stats_file.write(f"  Best response: {best_response}\n")
                stats_file.write(f"  Worst response: {worst_response}\n")
                stats_file.write("\n")
        else:
            # Write statistics when no valid grade sets exist
            with open(STATISTICS_FILE, "a") as stats_file:
                stats_file.write(f"Combination {key}:\n")
                stats_file.write(f"  Total components: {total_count}\n")
                stats_file.write(f"  Valid components: {valid_count}\n")
                stats_file.write(f"  Invalid components: {invalid_count}\n")
                stats_file.write(f"  Validity percentage: {validity_percentage:.2f}%\n")
                stats_file.write(f"  No valid grade sets found\n\n")


def _get_score_from_grades(grades: list[float]) -> float:
    return 100 * grades[-1] + sum(grades)


if __name__ == "__main__":
    main()
