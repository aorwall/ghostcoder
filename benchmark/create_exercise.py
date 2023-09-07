import json
import logging
import random
from pathlib import Path
from typing import List, Optional

from benchmark.benchmark import Benchmark, run_python_unittest, BenchmarkExerciseResult
from benchmark.model import Difficulty
from benchmark.prompts import BUSINESS_AREAS, SKILLS, INSTRUCTION_SYSTEM_PROMPT, INSTRUCTION_FEW_SHOTS, \
    CREATE_BUSINESS_INSTRUCTION_PROMPT, REVIEW_INSTRUCTION_SYSTEM_PROMPT, \
    WRITE_TEST_AND_STUB_SYSTEM_PROMPT, WRITE_TEST_AND_STUB_PROMPT, \
    VERIFY_AFTER_TEST_SYSTEM_PROMPT, VERIFY_AFTER_TEST_NO_CHANGES_PROMPT, VERIFY_TEST_SYSTEM_PROMPT, \
    VERIFY_TEST_SUIT_FEW_SHOTS
from benchmark.utils import create_openai_client
from ghostcoder import FileRepository
from ghostcoder.actions import WriteCodeAction
from ghostcoder.schema import Message, TextItem, FileItem

logging.basicConfig(level=logging.INFO)

benchmark_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark")
log_dir = benchmark_dir / "prompt_log"
exercises_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark/exercises")
repository = FileRepository(repo_path=str(exercises_dir), use_git=False)

basic_llm_name = "gpt-3.5-turbo"
smart_llm_name = "gpt-4"


def create_business_request(skill: str, difficulty: Difficulty, business_area: str = None):
    if not business_area:
        business_area = random.choice(BUSINESS_AREAS)

    return CREATE_BUSINESS_INSTRUCTION_PROMPT.format(
        business_area=business_area,
        skill=skill,
        difficulty=difficulty.value)


def create_instruction(instruction_format: str = "tech-details", request: str = None, skill: str = None, difficulty: Difficulty = None, retry: int = 0) -> str:
    llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=1.0)
    action = WriteCodeAction(llm=llm, repository=repository, sys_prompt=INSTRUCTION_SYSTEM_PROMPT, auto_mode=True)

    if not skill:
        skill = random.choice(SKILLS)

    if not difficulty:
        difficulty = random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])

    if not request:
        request = create_business_request(skill=skill, difficulty=difficulty)

    logging.info(f"create_instruction(): Create new instruction with request:\n{request}")

    message = Message(sender="Human", items=[
        TextItem(text=request)
    ])

    response_messages = action.execute(message=message, message_history=INSTRUCTION_FEW_SHOTS)
    response_message = response_messages[-1]

    for item in response_message.find_items_by_type("updated_file"):
        if item.file_path.endswith("/instructions.md"):
            path_parts = item.file_path.split('/')
            if len(path_parts) > 1:
                exercise = path_parts[-2]
                with open("data.json", "w") as json_file:
                    data = {
                        "instruction_format": instruction_format,
                        "exercise": exercise,
                        "difficulty": difficulty.value,
                        "skill": skill
                    }
                    json.dump(data, json_file, indent=2)

    if retry < 3:
        logging.warning(f"create_instruction(): No instruction file with the proper file name `instructions.md` found "
                        f"in the response on retry {retry}, will try again. The response was:"
                        f"\n{response_messages[-1].to_prompt()}")
        return create_instruction(request=request, skill=skill, difficulty=difficulty, retry=retry + 1)

    raise Exception("Couldn't create instruction")


def review_instruction(exercise: str):
    llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=0.0)
    action = WriteCodeAction(llm=llm, repository=repository, sys_prompt=REVIEW_INSTRUCTION_SYSTEM_PROMPT, auto_mode=True)

    instruction_file = f"{exercise}/instructions.md"

    logging.info(f"review_instruction(): Review the instructions in {instruction_file}...")

    message = Message(sender="Human", items=[
        FileItem(file_path=instruction_file)
    ])

    response_messages = action.execute(message=message)

    logging.info(f"review_instruction(): Response:\n{response_messages[-1].to_prompt()}")


def create_tests_and_stub(exercise: str, language: str = "python", retry: int = 0):
    llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=0.0)
    action = WriteCodeAction(llm=llm, repository=repository, sys_prompt=WRITE_TEST_AND_STUB_SYSTEM_PROMPT, auto_mode=True)

    logging.info(f"create_tests_and_stub(): Create test suite and stub exercise {exercise} in {language} ..")

    instruction_file = f"{exercise}/instructions.md"

    # FIXME: not only python
    test_file = f"{exercise}/{language}/{exercise}_test.py"
    stub_file = f"{exercise}/{language}/{exercise}.py"

    message = Message(sender="Human", items=[
        TextItem(text=WRITE_TEST_AND_STUB_PROMPT.format(language=language)),
        FileItem(file_path=instruction_file),
        FileItem(file_path=test_file),
        FileItem(file_path=stub_file),
    ])

    response_messages = action.execute(message=message)
    response_message = response_messages[-1]

    found_files = set()
    target_files = {test_file, stub_file}

    for item in response_message.find_items_by_type("updated_file"):
        if item.file_path in target_files:
            found_files.add(item.file_path)

        if target_files.issubset(found_files):
            logging.info(f"create_tests_and_stub(): {found_files} where successfully created..")

            return

    if retry < 3:
        logging.warning(f"create_tests_and_stub(): The files {found_files} was returned, expected {target_files}, "
                        f"will try again. The response was:\n{response_messages[-1].to_prompt()}")
        return create_tests_and_stub(exercise=exercise, retry=retry+1)

    raise Exception("Couldn't create instruction")


def run_and_verify_exercise(exercise: str):
    logging.info(f"run_and_verify_exercise({exercise})")
    benchmark_result_dir = benchmark_dir / "test_results"
    log_dir = benchmark_result_dir / "prompt_log"

    results = []

    temperature = 0.0
    smart_llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=temperature)
    benchmark = Benchmark(
        llm=smart_llm,
        model_name=smart_llm_name,
        exercises_dir=exercises_dir,
        benchmarks_dir=benchmark_result_dir,
        log_dir=log_dir,
        run_tests=run_python_unittest
    )
    result = benchmark.run_exercise(exercise)
    results.append(result)

    retries = 0
    while not result.success:
        logging.info(f"run_and_verify_exercise({exercise}) First test run failed, will check if tests needs to be fixed (retries: {retries})")
        if review_test_suite(exercise):
            logging.info(f"run_and_verify_exercise({exercise}) Tests was fixed, will run again")
            retries = 0
        else:
            logging.info(f"run_and_verify_exercise({exercise}) Tests was not fixed, will retry")
        result = benchmark.run_exercise(exercise)
        results.append(result)

        if retries > 3:
            logging.info(f"run_and_verify_exercise({exercise}) Tried to fix tests {retries} times, giving up")
            return results

        retries += 1


    for i in range(5):
        llm = create_openai_client(log_dir=log_dir, llm_name=basic_llm_name, temperature=temperature)

        benchmark = Benchmark(
            llm=llm,
            model_name=basic_llm_name,
            exercises_dir=exercises_dir,
            benchmarks_dir=benchmark_result_dir,
            log_dir=log_dir,
            run_tests=run_python_unittest
        )

        result = benchmark.run_exercise(exercise)
        results.append(result)

        temperature += 0.2

    failed_test_count = len([result for result in results if result.test_failure])
    logging.info(f"{failed_test_count} of the benchmarks failed when implemented by {basic_llm_name}")

    return results


def review_failed_benchmark(result: BenchmarkExerciseResult, implementation_content: str, language: str = "python") -> bool:
    llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0)
    action = WriteCodeAction(llm=llm,
                             repository=repository,
                             sys_prompt=VERIFY_AFTER_TEST_SYSTEM_PROMPT,
                             auto_mode=True)

    logging.info(f"Review {result.exercise} with argument {result.no_change_arguments}")

    instruction_file = f"{result.exercise}/instructions.md"

    # FIXME: not only python
    test_file = f"{result.exercise}/{language}/{result.exercise}_test.py"
    stub_file = f"{result.exercise}/{language}/{result.exercise}.py"

    items = [
        TextItem(text=VERIFY_AFTER_TEST_NO_CHANGES_PROMPT.format(
            implementation_file=stub_file,
            test_output=result.test_failure)),
    ]

    if result.no_change_arguments:
        items.append(TextItem(text=result.no_change_arguments))

    items.extend([
        FileItem(file_path=instruction_file),
        FileItem(file_path=test_file),
        FileItem(file_path=stub_file, content=implementation_content, readonly=True)
    ])

    message = Message(sender="Human", items=items)

    response_messages = action.execute(message=message)
    response_message = response_messages[-1]
    updated_files = response_message.find_items_by_type("updated_file")
    if len(updated_files):
        logging.info(f"Did corrections to {len(updated_files)}")
        return True


def review_test_suite(exercise: str, language: str = "python") -> bool:
    llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0)
    action = WriteCodeAction(llm=llm,
                             repository=repository,
                             sys_prompt=VERIFY_TEST_SYSTEM_PROMPT,
                             auto_mode=True)

    logging.info(f"review_test_suite({exercise}): Review test suite")

    instruction_file = f"{exercise}/instructions.md"

    # FIXME: not only python
    test_file = f"{exercise}/{language}/{exercise}_test.py"

    message = Message(sender="Human",
                      items=[
                          FileItem(file_path=instruction_file, readonly=True),
                          FileItem(file_path=test_file)
                      ])

    response_messages = action.execute(message=message, message_history=VERIFY_TEST_SUIT_FEW_SHOTS)
    response_message = response_messages[-1]
    updated_files = [item.file_path for item in response_message.find_items_by_type("updated_file")]
    if len(updated_files):
        logging.info(f"review_test_suite({exercise}): Did corrections to {updated_files}")
        return True
    else:
        return False


def review_benchmark_results(exercise: str, results: List[BenchmarkExerciseResult], language: str = "python") -> bool:
    #with open("data.json", "r") as json_file:
    #    data_loaded = json.load(json_file)
    #    print(data_loaded)

    success_count_basic = len(
        [result for result in results if result.llm_name == basic_llm_name and not result.test_failure])
    failed_count_basic = len(
        [result for result in results if result.llm_name == basic_llm_name and result.test_failure])
    success_count_smart = len(
        [result for result in results if result.llm_name == smart_llm_name and not result.test_failure])

    if failed_count_basic == 0:
        logging.info(f"All {success_count_basic} benchmark runs succeeded, verify that we have sufficient tests")
        corrected = review_test_suite(exercise)
        if corrected:
            return False

    if success_count_basic == 0 and success_count_smart == 0:
        results_to_check = [result for result in results if result.llm_name == smart_llm_name and result.test_failure]
    else:
        results_to_check = [result for result in results if result.no_change_arguments]

    no_change_implementations = set()
    correction_count = 0
    for no_change_result in results_to_check:
        implementation_file = Path(no_change_result.result_dir / f"{language}/{no_change_result.exercise}.py")
        implementation_content = implementation_file.read_text()
        if implementation_content not in no_change_implementations:
            did_corrections = review_failed_benchmark(no_change_result, implementation_content, language=language)
            if correction_count:
                did_corrections += 1
        else:
            logging.info(f"Change argument already handled: {no_change_result.no_change_arguments}")

    if correction_count:
        return False

    difficulty = None
    if failed_count_basic == 0:
        logging.info(f"All {success_count_basic} benchmark runs succeeded, set level to EASY")
        difficulty = Difficulty.EASY
    elif success_count_basic > 0:
        logging.info(f"At least one {success_count_basic} benchmark runs succeeded, will set difficulty level to MEDIUM")
        difficulty = Difficulty.MEDIUM
    elif success_count_smart > 0:
        logging.info(f"At least one {success_count_smart} benchmark runs succeeded, will set difficulty level to HARD")
        difficulty = Difficulty.HARD

    #if difficulty and difficulty != data_loaded["difficulty"]:
    #    logging.info(f"Change level of difficulty from {data_loaded['difficulty']} to {difficulty}")

    return True

