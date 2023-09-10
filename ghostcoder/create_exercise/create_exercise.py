import json
import logging
import random
import sys
import time
from pathlib import Path
from typing import List, Optional

from IPython.core.display import Pretty
from IPython.core.display_functions import update_display
from IPython.display import display, Markdown
from tqdm.notebook import tqdm

from benchmark.benchmark import Benchmark, BenchmarkResult
from benchmark.model import Difficulty
from benchmark.prompts import BUSINESS_AREAS, SKILLS, INSTRUCTION_SYSTEM_PROMPT, INSTRUCTION_FEW_SHOTS, \
    CREATE_BUSINESS_INSTRUCTION_PROMPT, REVIEW_INSTRUCTION_SYSTEM_PROMPT, \
    WRITE_TEST_AND_SOLUTION_SYSTEM_PROMPT, WRITE_TEST_AND_SOLUTION_PROMPT, \
    VERIFY_AFTER_TEST_SYSTEM_PROMPT, VERIFY_AFTER_TEST_NO_CHANGES_PROMPT, VERIFY_TEST_SYSTEM_PROMPT, \
    VERIFY_TEST_SUIT_FEW_SHOTS, CREATE_STUBS_SYSTEM_PROMPT, CREATE_STUBS_FEW_SHOTS
from benchmark.utils import create_openai_client
from ghostcoder import FileRepository
from ghostcoder.actions import WriteCodeAction
from ghostcoder.schema import Message, TextItem, FileItem, Item
from ghostcoder.verify.verify_python_unittest import PythonUnittestVerifier


def setup_logging():
    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s - %(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(stream_handler)
    logging.getLogger().setLevel(logging.INFO)

#setup_logging()

logger = logging.getLogger(__name__)

benchmark_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark")
log_dir = benchmark_dir / "prompt_log"
exercises_dir = Path("/home/albert/repos/albert/ghostcoder-lite/new_exercises")
repository = FileRepository(repo_path=str(exercises_dir), use_git=False)

basic_llm_name = "gpt-3.5-turbo"
smart_llm_name = "gpt-4"


def create_business_request(skill: str = None, difficulty: Difficulty = None, business_area: str = None):
    if not skill:
        skill = random.choice(SKILLS)

    if not difficulty:
        difficulty = random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])

    if not business_area:
        business_area = random.choice(BUSINESS_AREAS)

    request = CREATE_BUSINESS_INSTRUCTION_PROMPT.format(
        business_area=business_area,
        skill=skill,
        difficulty=difficulty.value)

    display(Markdown(request))

    return request


def create_instruction(request: str, instruction_format: str = "tech-details", retry: int = 0) -> str:
    llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=1.0)
    action = WriteCodeAction(llm=llm, repository=repository, sys_prompt=INSTRUCTION_SYSTEM_PROMPT, auto_mode=True, expect_one_file=True)

    logger.info(f"Create new instruction")

    message = Message(sender="Human", items=[
        TextItem(text=request)
    ])

    response_messages = action.execute(message=message, message_history=[])
    response_message = response_messages[-1]

    exercise = None
    for item in response_message.find_items_by_type("updated_file"):
        if item.file_path.endswith("/instructions.md"):
            path_parts = item.file_path.split('/')
            if len(path_parts) > 1:
                exercise = path_parts[-2].lower()

    if exercise:
        info_file = Path(exercises_dir / exercise / "info.json")
        with open(info_file, "w") as json_file:
            data = {
                "instruction_format": instruction_format,
                "exercise": exercise
            }
            json.dump(data, json_file, indent=2)

        logger.info(f"Created instruction for exercise {exercise}")

        for item in response_message.items:
            if "file" in item.type and not item.language:
                content = f"**{item.file_path}**\n{item.content}\n"
                display(Markdown(content))
            if item.type == "text":
                display(Markdown(item.to_prompt()))

        return exercise

    if retry < 3:
        logger.warning(f"No instruction file with the proper file name `instructions.md` found "
                       f"in the response on retry {retry}, will try again. The response was:"
                       f"\n{response_message.to_prompt()}")
        return create_instruction(request=request, retry=retry + 1)

    raise Exception("Couldn't create instruction")


def display_response(response_message: Message):
    for item in response_message.items:
        if "file" in item.type and not item.language:
            content = f"**{item.file_path}**\n{item.content}\n"
            display(Markdown(content))
        else:
            display(Markdown(item.to_prompt()))

def review_instruction(exercise: str):
    llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=0.0)
    action = WriteCodeAction(llm=llm, repository=repository, sys_prompt=REVIEW_INSTRUCTION_SYSTEM_PROMPT,
                             auto_mode=True, expect_one_file=True)

    instruction_file = f"{exercise}/instructions.md"

    logger.info(f"Review the instructions in {instruction_file}...")

    message = Message(sender="Human", items=[
        FileItem(file_path=instruction_file)
    ])

    response_messages = action.execute(message=message)
    response_message = response_messages[-1]

    # TODO: Verify response

    display_response(response_message)

def create_tests_and_implementation(exercise: str, language: str = "python", retry: int = 0):
    llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=0.0)
    action = WriteCodeAction(
        llm=llm,
        repository=repository,
        sys_prompt=WRITE_TEST_AND_SOLUTION_SYSTEM_PROMPT,
        auto_mode=True,
        verifier=PythonUnittestVerifier(test_file_pattern="*_test.py",
                                        current_dir=Path(exercises_dir / exercise / language)))

    if not retry:
        display(Markdown(f"Create test suite and implementation for exercise *{exercise}* using *{language}*."),
                display_id="create_tests_and_implementation")

    logger.info(
        f"Create test suite and implementation for exercise {exercise} in {language}")

    instruction_file = f"{exercise}/instructions.md"

    # FIXME: not only python
    test_file = f"{exercise}/{language}/{exercise}_test.py"
    impl_file = f"{exercise}/{language}/{exercise}.py"

    message = Message(sender="Human", items=[
        TextItem(text=WRITE_TEST_AND_SOLUTION_PROMPT.format(language=language)),
        FileItem(file_path=instruction_file),
        FileItem(file_path=test_file),
        FileItem(file_path=impl_file),
    ])

    response_messages = action.execute(message=message)
    if response_messages[-1].sender == "Human":
        update_display(
            Markdown(
                f"_Couldn't create a test suite and implementation based on instructions in `{instruction_file}` "
                f"that passed the tests. Call this function again to try again or create a new instruction._"),
            display_id="create_tests_and_implementation")

        display_response(response_messages[-1])
        return

    found_files = set()
    target_files = {test_file, impl_file}

    for response_message in response_messages:
        for item in response_message.find_items_by_type("updated_file"):
            if item.file_path in target_files:
                found_files.add(item.file_path)

            if target_files.issubset(found_files):
                logger.info(f"{found_files} where successfully created..")
                update_display(
                    Markdown(f"Test suite and implementation based on instructions in `{instruction_file}` successfully created."),
                    display_id="create_tests_and_implementation")
                display_response(response_message)
                return

    if retry < 0:
        logger.warning(
            f"The files {found_files} was returned, expected {target_files}, "
            f"will try again. The response was:\n{response_messages[-1].to_prompt()}")
        update_display(
            Markdown(
                f"The files {found_files} was returned, expected {target_files}, will try again..."),
            display_id="create_tests_and_implementation")

        return create_tests_and_implementation(exercise=exercise, retry=retry + 1)

    raise Exception("Couldn't create instruction")


def review_test_suite(exercise: str, language: str = "python") -> bool:
    llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0)

    action = WriteCodeAction(llm=llm,
                             repository=repository,
                             sys_prompt=VERIFY_TEST_SYSTEM_PROMPT,
                             auto_mode=True,
                             verifier=PythonUnittestVerifier(test_file_pattern="*_test.py",
                                                             current_dir=Path(exercises_dir / exercise / language)))

    logger.info(f"review_test_suite({exercise}): Review test suite")

    instruction_file = f"{exercise}/instructions.md"

    # FIXME: not only python
    test_file = f"{exercise}/{language}/{exercise}_test.py"
    stub_file = f"{exercise}/{language}/{exercise}.py"

    message = Message(sender="Human",
                      items=[
                          FileItem(file_path=instruction_file),
                          FileItem(file_path=stub_file),
                          FileItem(file_path=test_file)
                      ])

    response_messages = action.execute(message=message, message_history=VERIFY_TEST_SUIT_FEW_SHOTS)
    response_message = response_messages[-1]
    if response_message.sender == "Human":
        display(
            Markdown(f"_The updated tests in `{test_file}` didn't pass the tests."
                     f" Call this function again to try again or create a new instruction._"),
            display_id="review_test_suite")

        display_response(response_message)
        return

    updated_files = [item.file_path for item in response_message.find_items_by_type("updated_file")]
    display_response(response_message)

    if len(updated_files):
        return True
    else:
        return False

def create_stubs(exercise: str, language: str = "python", retry: int = 0):
    llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=0.0)
    action = WriteCodeAction(
        llm=llm,
        repository=repository,
        sys_prompt=CREATE_STUBS_SYSTEM_PROMPT,
        auto_mode=True
    )

    logger.info(f"create_stubs(): Create stub files for {exercise} in {language}")

    instruction_file = f"{exercise}/instructions.md"

    # FIXME: not only python
    test_file = f"{exercise}/{language}/{exercise}_test.py"
    impl_file = f"{exercise}/{language}/{exercise}.py"
    stub_file = f"{exercise}/{language}/stubs/{exercise}.py"
    stub_with_comments = f"{exercise}/{language}/stubs_with_comments/{exercise}.py"

    message = Message(sender="Human", items=[
        FileItem(file_path=instruction_file),
        FileItem(file_path=test_file),
        FileItem(file_path=impl_file),
        FileItem(file_path=stub_file),
        FileItem(file_path=stub_with_comments),
    ])

    response_messages = action.execute(message=message, message_history=CREATE_STUBS_FEW_SHOTS)
    response_message = response_messages[-1]

    found_files = set()
    target_files = {stub_file, stub_with_comments}

    for item in response_message.find_items_by_type("updated_file"):
        if item.file_path in target_files:
            found_files.add(item.file_path)

        if target_files.issubset(found_files):
            logger.info(f"create_stubs(): {found_files} where successfully created..")
            display_response(response_message)
            return

    if retry < 0:
        logger.warning(f"create_stubs(): The files {found_files} was returned, expected {target_files}, "
                       f"will try again. The response was:\n{response_messages[-1].to_prompt()}")
        return create_tests_and_implementation(exercise=exercise, retry=retry + 1)

    raise Exception("Couldn't create stub")

def run_and_verify_exercise(exercise: str):
    tries = 5
    benchmark_result_dir = benchmark_dir / "test_results"
    benchmark_result_dir.mkdir(parents=True, exist_ok=True)
    log_dir = benchmark_result_dir / "prompt_log"

    results = []
    reviewer_llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0)

    progress_bar = tqdm(range(tries))

    temperature = 0.0
    for i in progress_bar:
        progress_bar.set_postfix({"llm": basic_llm_name, "temperature": temperature}, refresh=True)

        llm = create_openai_client(log_dir=log_dir, llm_name=basic_llm_name, temperature=temperature)

        benchmark = Benchmark(
            llm=llm,
            llm_name=basic_llm_name,
            llm_params={"temperature": temperature},
            exercises_dir=exercises_dir,
            benchmarks_dir=benchmark_result_dir,
            reviewer_llm=reviewer_llm
        )

        result = benchmark.run_exercise(exercise)
        results.append(result)

        if result.success:
            display(Markdown(f"Test run {i + 1}/{tries} with temperature {temperature} succeeded."))
        else:
            test_failures = ""
            display(Markdown(f"Test run {i + 1}/{tries} with temperature {temperature} failed. {test_failures}"))

        temperature += 0.2

    failed_test_count = len([result for result in results if not result.success])
    if failed_test_count == len(results):
        tries = 3
        display(Markdown(f"All {len(results)} of the benchmarks failed when implemented by `{basic_llm_name}`, "
                    f"will try to test {tries} times with `{smart_llm_name}`"))

        progress_bar = tqdm(range(tries))

        for i in progress_bar:
            progress_bar.set_postfix({"llm": smart_llm_name, "temperature": temperature}, refresh=True)

            llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=temperature)
            benchmark = Benchmark(
                llm=llm,
                llm_name=smart_llm_name,
                llm_params={"temperature": temperature},
                exercises_dir=exercises_dir,
                benchmarks_dir=benchmark_result_dir,
                reviewer_llm=reviewer_llm
            )

            result = benchmark.run_exercise(exercise)
            results.append(result)

            temperature += 0.2
    else:
        display(Markdown(
            f"{failed_test_count} out of {len(results)} of the benchmarks failed when implemented by {basic_llm_name}"))

    benchmark_results = []
    for result in results:
        benchmark_result = {
            "llm_name": result.llm_name,
            "llm_params": result.llm_params,
            "success": result.success,
            "retries": result.retries,
        }

        if not result.success:
            if result.verification_result:
                benchmark_result["test_failures"] = [failure.test_method for failure in
                                                     result.verification_result.failures]
            if result.no_change_arguments:
                benchmark_result["no_change_arguments"] = True

        benchmark_results.append(benchmark_result)

    info_file = Path(exercises_dir / exercise / "info.json")
    with open(info_file, "r") as json_file:
        info = json.load(json_file)

    info["benchmark_results"] = benchmark_results

    with open(info_file, "w") as json_file:
        logger.info(f"run_and_verify_exercise({exercise}): Write benchmark results to {info_file}")
        json.dump(info, json_file, indent=2)

    return results



def review_failed_benchmark(exercise: str, review_items: List[Item], language: str = "python") -> bool:
    llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0)
    action = WriteCodeAction(llm=llm,
                             repository=repository,
                             sys_prompt=VERIFY_AFTER_TEST_SYSTEM_PROMPT,
                             auto_mode=True)

    logger.info(f"Review {exercise} with {len(review_items)} review items")

    instruction_file = f"{exercise}/instructions.md"

    # FIXME: not only python
    test_file = f"{exercise}/{language}/{exercise}_test.py"
    impl_file = f"{exercise}/{language}/{exercise}.py"
    stub_file = f"{exercise}/{language}/stubs/{exercise}.py"
    stub_with_comments = f"{exercise}/{language}/stub_with_comments/{exercise}.py"

    message = Message(sender="Human", items=[
        FileItem(file_path=instruction_file),
        FileItem(file_path=test_file),
        FileItem(file_path=impl_file),
        FileItem(file_path=stub_file),
        FileItem(file_path=stub_with_comments),
    ])

    message.items.extend(review_items)

    response_messages = action.execute(message=message)
    response_message = response_messages[-1]
    updated_files = response_message.find_items_by_type("updated_file")
    if len(updated_files):
        logger.info(f"Did corrections to {len(updated_files)}")
        return True



def review_benchmark_results(exercise: str, results: List[BenchmarkResult], language: str = "python") -> bool:
    success_count_basic = len(
        [result for result in results if result.llm_name == basic_llm_name and result.success])
    failed_count_basic = len(
        [result for result in results if result.llm_name == basic_llm_name and not result.success])
    success_count_smart = len(
        [result for result in results if result.llm_name == smart_llm_name and result.success])

    if failed_count_basic == 0:
        logger.info(f"All {success_count_basic} benchmark runs succeeded, verify that we have sufficient tests")
        corrected = review_test_suite(exercise)
        if corrected:
            return False

    review_items = []
    no_change_arguments = []
    outputs = set()

    for result in results:
        if result.verification_result:
            for failure in result.verification_result.failures:
                if failure.output not in outputs:
                    review_items.append(failure)
                    outputs.add(failure.output)

        if result.no_change_arguments:
            no_change_arguments.append(TextItem(text=result.no_change_arguments))

    if review_items:
        return review_failed_benchmark(exercise, review_items, language=language)

    difficulty = None
    if failed_count_basic == 0:
        logger.info(f"All {success_count_basic} benchmark runs succeeded, set level to EASY")
        difficulty = Difficulty.EASY
    elif success_count_basic > 0:
        logger.info(f"At least one {success_count_basic} benchmark runs succeeded, will set difficulty level to MEDIUM")
        difficulty = Difficulty.MEDIUM
    elif success_count_smart > 0:
        logger.info(f"At least one {success_count_smart} benchmark runs succeeded, will set difficulty level to HARD")
        difficulty = Difficulty.HARD

    info_file = Path(exercises_dir / exercise / "info.json")
    with open(info_file, "r") as json_file:
        info = json.load(json_file)

    info["difficulty"] = difficulty

    with open(info_file, "w") as json_file:
        logger.info(f"Write benchmark results to {info_file}")
        json.dump(info, json_file, indent=2)

    return False
