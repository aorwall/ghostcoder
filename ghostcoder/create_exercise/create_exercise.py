import json
import logging
import random
from pathlib import Path
from typing import List, Optional

from IPython.core.display import Pretty
from IPython.display import display, Markdown
from langchain.chat_models import ChatOpenAI
from tqdm.notebook import tqdm

from ghostcoder.benchmark.benchmark import Benchmark, BenchmarkResult
from ghostcoder.callback import LogCallbackHandler
from ghostcoder.llm import ChatLLMWrapper, LLMWrapper
from ghostcoder.schema import Difficulty
from ghostcoder.create_exercise.prompts import BUSINESS_AREAS, SKILLS, INSTRUCTION_SYSTEM_PROMPT, \
    CREATE_BUSINESS_INSTRUCTION_PROMPT, REVIEW_INSTRUCTION_SYSTEM_PROMPT, \
    WRITE_TEST_AND_SOLUTION_SYSTEM_PROMPT, \
    VERIFY_AFTER_TEST_SYSTEM_PROMPT, VERIFY_TEST_SYSTEM_PROMPT, \
    VERIFY_TEST_SUIT_FEW_SHOTS, CREATE_STUBS_SYSTEM_PROMPT, CREATE_STUBS_FEW_SHOTS
from ghostcoder import FileRepository
from ghostcoder.actions import WriteCodeAction
from ghostcoder.schema import Message, TextItem, FileItem, Item
from ghostcoder.verify.verify_python_unittest import PythonUnittestVerifier

logger = logging.getLogger("ghostcoder.create_exercise")


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

def display_response(response_message: Message):
    for item in response_message.items:
        if "file" in item.type and not item.language:
            content = f"**{item.file_path}**\n{item.content}\n"
            display(Markdown(content))
        else:
            display(Markdown(item.to_prompt()))

class ExerciseBuilder:

    def __init__(self,
                 exercises_dir: Path,
                 benchmark_results_dir: Path,
                 prompt_log_dir: Path = None,
                 exercise: str = None,
                 basic_llm_name: str = "gpt-3.5-turbo",
                 smart_llm_name: str = "gpt-4"):
        self.exercises_dir = exercises_dir

        if not prompt_log_dir:
            self.prompt_log_dir = exercises_dir / ".prompt_log"

        self.benchmark_results_dir = benchmark_results_dir
        self.repository = FileRepository(repo_path=str(exercises_dir), use_git=False)
        self.exercise = exercise
        self.basic_llm_name = basic_llm_name
        self.smart_llm_name = smart_llm_name

    @property
    def exercise_dir(self):
        return self.exercises_dir / self.exercise

    def create_instruction(self, request: str, instruction_format: str = "tech-details"):
        if self.exercise:
            raise Exception(f"An instruction already created for the exercise {self.exercise}")

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=1.0)
        action = self.create_coder_writer(llm=llm, sys_prompt=INSTRUCTION_SYSTEM_PROMPT, expect_one_file=True, allow_hallucinated_files=True)

        display(Pretty(f"Creating new instruction using {self.smart_llm_name} with temperature set to 1.0..."))

        message = Message(sender="Human", items=[
            TextItem(text=request)
        ])

        response_messages = action.execute(message=message, message_history=[])
        response_message = response_messages[-1]

        exercise = None
        for item in response_message.find_items_by_type("updated_file"):
            # TODO: Handle files saved in the wrong way
            if item.file_path.endswith("/instructions.md"):
                path_parts = item.file_path.split('/')
                if len(path_parts) > 1:
                    exercise = path_parts[-2].lower()

        if not exercise:
            raise Exception("Couldn't create instruction")

        self.exercise = exercise

        info_file = self.exercise_dir / "info.json"
        with open(info_file, "w") as json_file:
            data = {
                "instruction_format": instruction_format,
                "exercise": exercise
            }
            json.dump(data, json_file, indent=2)

        logger.info(f"Created instruction for exercise {self.exercise}")

        for item in response_message.items:
            if "file" in item.type and not item.language:
                content = f"**{item.file_path}**\n{item.content}\n"
                display(Markdown(content))
            if item.type == "text":
                display(Markdown(item.to_prompt()))

    def assert_exercise(self):
        if not self.exercise:
            raise ValueError("No exercise created yet")

    def review_instruction(self):
        if not (self.exercise_dir / "instructions.md").exists():
            raise Exception(f"{self.exercise_dir / 'instructions.md'} not found.")

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)
        action = self.create_coder_writer(llm=llm, sys_prompt=REVIEW_INSTRUCTION_SYSTEM_PROMPT, expect_one_file=True)

        instruction_file = f"{self.exercise}/instructions.md"

        logger.info(f"Review the instructions in {instruction_file}...")

        message = Message(sender="Human", items=[
            FileItem(file_path=instruction_file)
        ])

        response_messages = action.execute(message=message)
        response_message = response_messages[-1]

        # TODO: Verify response

        display_response(response_message)

    def create_tests_and_implementation(self, language: str = "python", retry: int = 0):
        self.assert_exercise()
        # TODO: Check for instruction file

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)

        verifier = None
        if language == "python":
            test_file = f"{self.exercise}/{language}/{self.exercise}_test.py"
            impl_file = f"{self.exercise}/{language}/{self.exercise}.py"
            verifier = PythonUnittestVerifier(test_file_pattern="*_test.py",
                                              current_dir=Path(self.exercises_dir / self.exercise / language))
            language_specifics = "* Use unittest for tests"
        elif language == "java":
            words = self.exercise.split('_')
            class_name = ''.join(word.capitalize() for word in words)
            test_file = f"{self.exercise}/{language}/{class_name}Test.java"
            impl_file = f"{self.exercise}/{language}/{class_name}.java"
            language_specifics = "* Use JUnit5 for tests"
        else:
            raise Exception(f"Unsupported language {language}")

        action = WriteCodeAction(llm=llm,
                                 sys_prompt=WRITE_TEST_AND_SOLUTION_SYSTEM_PROMPT.format(
                                     language=language, language_specifics=language_specifics),
                                 repository=self.repository,
                                 auto_mode=True, verifier=verifier)

        if not retry:
            display(Pretty(f"Create test suite and implementation for exercise {self.exercise} in {language}."))

        logger.info(
            f"Create test suite and implementation for exercise {self.exercise} in {language}")

        instruction_file = f"{self.exercise}/instructions.md"

        message = Message(sender="Human", items=[
            FileItem(file_path=instruction_file),
            FileItem(file_path=test_file),
            FileItem(file_path=impl_file),
        ])

        response_messages = action.execute(message=message)
        if response_messages[-1].sender == "Human":
            display(
                Markdown(
                    f"Couldn't create a test suite and implementation based on instructions in `{instruction_file}` "
                    f"that passed the tests. Call this function again to try again or create a new instruction._"))

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
                    display(
                        Pretty(f"Test suite and implementation based on instructions in `{instruction_file}` successfully created."))
                    display_response(response_message)
                    return

        if retry < 0:
            logger.warning(
                f"The files {found_files} was returned, expected {target_files}, "
                f"will try again. The response was:\n{response_messages[-1].to_prompt()}")
            display(
                Pretty(
                    f"The files {found_files} was returned, expected {target_files}, will try again..."),
                display_id="create_tests_and_implementation")

            return self.create_tests_and_implementation(retry=retry + 1)

        raise Exception("Couldn't create instruction")

    def review_test_suite(self, language: str = "python"):
        self.assert_exercise()
        # TODO: Check for test and implementation files

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)

        action = WriteCodeAction(llm=llm, sys_prompt=VERIFY_TEST_SYSTEM_PROMPT, repository=self.repository,
                                 auto_mode=True, verifier=PythonUnittestVerifier(test_file_pattern="*_test.py",
                                                                                 current_dir=Path(
                                                                                     self.exercises_dir / self.exercise / language)))

        logger.info(f"review_test_suite({self.exercise}): Review test suite")

        instruction_file = f"{self.exercise}/instructions.md"

        files = [FileItem(file_path=f"{language}/{f.name}", content=f.read_text())
                 for f in (self.exercise_dir / language).iterdir() if f.is_file()]

        message = Message(sender="Human", items=[FileItem(file_path=instruction_file)] + files)

        response_messages = action.execute(message=message, message_history=VERIFY_TEST_SUIT_FEW_SHOTS)
        response_message = response_messages[-1]
        if response_message.sender == "Human":
            display(
                Markdown(f"_The updated tests didn't pass the tests. "
                         f"Call this function again to try again or create a new instruction._"),
                display_id="review_test_suite")

            display_response(response_message)
            return

        display_response(response_message)

    def create_stubs(self, language: str = "python"):
        self.assert_exercise()
        # TODO: Check for test and implementation files

        llm = self.create_openai_client(llm_name="gpt-4", temperature=0.0)
        action = self.create_coder_writer(llm=llm, sys_prompt=CREATE_STUBS_SYSTEM_PROMPT, expect_one_file=True)

        display(Pretty(f"Create stub files for {self.exercise} in {language}"))

        instruction_file = f"{self.exercise}/instructions.md"

        target_files = set()
        files = []
        for file in (self.exercise_dir / language).iterdir():
            if file.is_file():
                files.append(FileItem(file_path=f"{self.exercise}/{language}/{file.name}", content=file.read_text(), readonly=True))
                if "test" not in file.name.lower():
                    stub_file = f"{self.exercise}/{language}/stubs/{file.name}"
                    stub_with_comments = f"{self.exercise}/{language}/stubs_with_comments/{file.name}"
                    files.append(FileItem(file_path=stub_file, content=file.read_text()))
                    files.append(FileItem(file_path=stub_with_comments, content=file.read_text()))
                    target_files.add(stub_file)
                    target_files.add(stub_with_comments)

        message = Message(sender="Human", items=[FileItem(file_path=instruction_file)] + files)
        response_messages = action.execute(message=message, message_history=CREATE_STUBS_FEW_SHOTS)
        response_message = response_messages[-1]

        found_files = set()
        for item in response_message.find_items_by_type("updated_file"):
            if item.file_path in target_files:
                found_files.add(item.file_path)

            if target_files.issubset(found_files):
                logger.info(f"create_stubs(): {found_files} where successfully created..")
                display_response(response_message)
                return

        raise Exception(f"The files {found_files} was returned, expected {target_files}, "
                        f"will try again. The response was:\n{response_messages[-1].to_prompt()}")

    def run_and_verify_exercise(self):
        self.assert_exercise()
        # TODO: Check for test, implementation and stub files

        tries = 5
        benchmark_result_dir = self.benchmark_results_dir / "test_results"
        benchmark_result_dir.mkdir(parents=True, exist_ok=True)

        results = []
        reviewer_llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)

        progress_bar = tqdm(range(tries))

        temperature = 0.0
        for i in progress_bar:
            progress_bar.set_postfix({"llm": self.basic_llm_name, "temperature": temperature}, refresh=True)

            llm = self.create_openai_client(llm_name=self.basic_llm_name, temperature=temperature)

            benchmark = Benchmark(
                llm=llm,
                llm_name=self.basic_llm_name,
                llm_params={"temperature": temperature},
                exercises_dir=self.exercises_dir,
                benchmarks_dir=benchmark_result_dir,
                reviewer_llm=reviewer_llm
            )

            result = benchmark.run_exercise(self.exercise)
            results.append(result)

            if result.success:
                display(Pretty(f"Test run {i + 1}/{tries} with temperature {temperature} succeeded."))
            else:
                test_failures = ""
                display(Pretty(f"Test run {i + 1}/{tries} with temperature {temperature} failed. {test_failures}"))

            temperature += 0.2

        failed_test_count = len([result for result in results if not result.success])
        if failed_test_count == len(results):
            tries = 3
            display(Pretty(f"All {len(results)} of the benchmarks failed when implemented by {self.basic_llm_name}, "
                           f"will try to test {tries} times with {self.smart_llm_name}"))

            temperature = 0.0
            progress_bar = tqdm(range(tries))

            for i in progress_bar:
                progress_bar.set_postfix({"llm": self.smart_llm_name, "temperature": temperature}, refresh=True)

                llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=temperature)
                benchmark = Benchmark(
                    llm=llm,
                    llm_name=self.smart_llm_name,
                    llm_params={"temperature": temperature},
                    exercises_dir=self.exercises_dir,
                    benchmarks_dir=benchmark_result_dir,
                    reviewer_llm=reviewer_llm
                )

                result = benchmark.run_exercise(self.exercise)
                results.append(result)

                temperature += 0.2
        else:
            display(Pretty(
                f"{failed_test_count} out of {len(results)} of the benchmarks failed when implemented by {self.basic_llm_name}"))

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

            if result.feedback and not result.feedback.tests_correct:
                benchmark_result["test_suite_feedback"] = result.feedback.tests_feedback

            benchmark_results.append(benchmark_result)

        info_file = self.exercise_dir / "info.json"
        with open(info_file, "r") as json_file:
            info = json.load(json_file)

        info["benchmark_results"] = benchmark_results

        with open(info_file, "w") as json_file:
            logger.info(f"run_and_verify_exercise({self.exercise}): Write benchmark results to {info_file}")
            json.dump(info, json_file, indent=2)


    def review_failed_benchmark(self, review_items: List[Item], language: str = "python") -> bool:
        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)
        action = self.create_coder_writer(llm=llm, sys_prompt=VERIFY_AFTER_TEST_SYSTEM_PROMPT)

        logger.info(f"Review {self.exercise} with {len(review_items)} review items")

        instruction_file = f"{self.exercise}/instructions.md"

        # FIXME: not only python
        test_file = f"{self.exercise}/{language}/{self.exercise}_test.py"
        impl_file = f"{self.exercise}/{language}/{self.exercise}.py"
        stub_file = f"{self.exercise}/{language}/stubs/{self.exercise}.py"
        stub_with_comments = f"{self.exercise}/{language}/stub_with_comments/{self.exercise}.py"

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


    def review_benchmark_results(self, results: List[BenchmarkResult], language: str = "python") -> bool:
        success_count_basic = len(
            [result for result in results if result.llm_name == self.basic_llm_name and result.success])
        failed_count_basic = len(
            [result for result in results if result.llm_name == self.basic_llm_name and not result.success])
        success_count_smart = len(
            [result for result in results if result.llm_name == self.smart_llm_name and result.success])

        if failed_count_basic == 0:
            logger.info(f"All {success_count_basic} benchmark runs succeeded, verify that we have sufficient tests")
            corrected = self.review_test_suite()
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
            return self.review_failed_benchmark(review_items, language=language)

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

        info_file = Path(self.exercises_dir / self.exercise / "info.json")
        with open(info_file, "r") as json_file:
            info = json.load(json_file)

        info["difficulty"] = difficulty

        with open(info_file, "w") as json_file:
            logger.info(f"Write benchmark results to {info_file}")
            json.dump(info, json_file, indent=2)

        return False

    def create_openai_client(self, llm_name: str, temperature: float):
        callback = LogCallbackHandler(str(self.prompt_log_dir))
        return ChatLLMWrapper(ChatOpenAI(
            model=llm_name,
            temperature=temperature,
            callbacks=[callback]
        ))

    def create_coder_writer(self,
                            llm: LLMWrapper,
                            sys_prompt: str = None,
                            expect_one_file: bool = False,
                            allow_hallucinated_files: bool = False):
        return WriteCodeAction(llm=llm,
                               sys_prompt=sys_prompt,
                               repository=self.repository,
                               auto_mode=True,
                               expect_one_file=expect_one_file,
                               allow_hallucinated_files=allow_hallucinated_files)
