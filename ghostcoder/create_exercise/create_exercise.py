import json
import logging
import random
import re
import shutil
from pathlib import Path
from typing import List

from IPython.core.display import Pretty
from IPython.display import display, Markdown
from langchain.chat_models import ChatOpenAI
from tqdm.notebook import tqdm

from ghostcoder import FileRepository
from ghostcoder.actions import CodeWriter
from ghostcoder.actions.write_code.base import StreamCallback
from ghostcoder.benchmark.benchmark import Benchmark, BenchmarkResult
from ghostcoder.callback import LogCallbackHandler
from ghostcoder.create_exercise.prompts import BUSINESS_AREAS, SKILLS, INSTRUCTION_SYSTEM_PROMPT, \
    CREATE_BUSINESS_INSTRUCTION_PROMPT, REVIEW_INSTRUCTION_SYSTEM_PROMPT, \
    WRITE_TEST_AND_SOLUTION_SYSTEM_PROMPT, \
    VERIFY_AFTER_TEST_SYSTEM_PROMPT, VERIFY_TEST_SYSTEM_PROMPT, \
    CREATE_STUBS_SYSTEM_PROMPT, CREATE_STUBS_PYTHON_RULES, \
    CREATE_STUBS_JAVA_RULES, DIRECTORY_NAME_PROMPT
from ghostcoder.ghostcoder import Ghostcoder
from ghostcoder.ipython_callback import DisplayCallback
from ghostcoder.llm import ChatLLMWrapper, LLMWrapper
from ghostcoder.schema import Difficulty
from ghostcoder.schema import Message, TextItem, FileItem, Item
from ghostcoder.test_tools import JavaMvnUnit5TestTool, PythonUnittestTestTool

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
        self.exercise = exercise
        self.basic_llm_name = basic_llm_name
        self.smart_llm_name = smart_llm_name
        self.display = DisplayCallback()

    @property
    def exercise_dir(self):
        return self.exercises_dir / self.exercise

    @property
    def repository(self):
        if self.exercise:
            return FileRepository(repo_path=self.exercise_dir, use_git=False) # TODO: use_git=True
        raise ValueError("No exercise created yet")

    def create_instruction(self, request: str, instruction_format: str = "tech-details"):
        if self.exercise:
            raise Exception(f"An instruction already created for the exercise {self.exercise}")

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=1.0)

        request_msg = Message(sender="Human", items=[
            TextItem(text=request)
        ])
        messages = [request_msg]

        self.display.display_message(request_msg)

        # TODO: Use Ghostcoder instead if History is implemented
        instructions, _ = llm.generate(sys_prompt=INSTRUCTION_SYSTEM_PROMPT, messages=messages, callback = StreamCallback(callback=self.display))

        instruction_msg = Message(sender="AI", items=[
            TextItem(text=instructions)
        ])
        messages.append(instruction_msg)

        self.display.display_message(instruction_msg)
        # TODO: Verify contents

        exercise_name_msg = Message(sender="Ghostcoder", items=[
            TextItem(text=DIRECTORY_NAME_PROMPT)
        ])
        messages.append(exercise_name_msg)
        self.display.display_message(exercise_name_msg)

        exercise, _ = llm.generate(
            sys_prompt=INSTRUCTION_SYSTEM_PROMPT,
            messages=messages,
            callback=StreamCallback(callback=self.display))

        self.display.display_message(Message(sender="AI", items=[
            TextItem(text=exercise)
        ]))

        pattern = re.compile(r"^[a-z0-9_]+$")
        if len(exercise) > 24 or not pattern.match(exercise):
            raise Exception(f"Invalid exercise name {exercise}")

        self.exercise = exercise
        self.exercise_dir.mkdir(parents=True, exist_ok=True)
        instruction_file = self.exercise_dir / "instructions.md"
        instruction_file.write_text(instructions)

        info_file = self.exercise_dir / "info.json"
        with open(info_file, "w") as json_file:
            data = {
                "instruction_format": instruction_format,
                "exercise": exercise
            }
            json.dump(data, json_file, indent=2)

        logger.info(f"Created instruction for exercise {self.exercise}")

        self.display.display("Ghostcoder", f"I saved the new exercise instructions to `{instruction_file}`.")

    def assert_exercise(self):
        if not self.exercise:
            raise ValueError("No exercise created yet")

    def review_instruction(self):
        if not (self.exercise_dir / "instructions.md").exists():
            raise Exception(f"{self.exercise_dir / 'instructions.md'} not found.")

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)
        ghostcoder = Ghostcoder(llm=llm,
                                code_writer_sys_prompt=REVIEW_INSTRUCTION_SYSTEM_PROMPT,
                                callback=self.display,
                                repository=self.repository)

        instruction_file = "instructions.md"

        logger.info(f"Review the instructions in {instruction_file}...")

        message = Message(sender="Human", items=[
            FileItem(file_path=instruction_file)
        ])

        response_messages = ghostcoder.run(message=message)
        response_message = response_messages[-1]

        # TODO: Verify response


    def create_tests_and_implementation(self, language: str = "python", retry: int = 0):
        self.assert_exercise()
        # TODO: Check for instruction file

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)

        language_dir = self.exercises_dir / self.exercise / language
        language_dir.mkdir(parents=True, exist_ok=True)

        if language == "python":
            test_file = f"/{language}/{self.exercise}_test.py"
            impl_file = f"/{language}/{self.exercise}.py"
            language_specifics = "* Use unittest for tests"
            test_tool = PythonUnittestTestTool(current_dir=language_dir, callback=self.display)
        elif language == "java":
            pom_xml = self.get_resource("no_deps/pom.xml")
            self.repository.update_file(f"{language}/pom.xml", pom_xml)
            words = self.exercise.split('_')
            class_name = ''.join(word.capitalize() for word in words)
            test_file = f"/{language}/src/test/java/{class_name}Test.java"
            impl_file = f"/{language}/src/main/java/{class_name}.java"
            language_specifics = "* Use JUnit5 for tests"
            test_tool = JavaMvnUnit5TestTool(current_dir=language_dir, callback=self.display)
        else:
            raise Exception(f"Unsupported language {language}")

        ghostcoder = Ghostcoder(llm=llm,
                                code_writer_sys_prompt=WRITE_TEST_AND_SOLUTION_SYSTEM_PROMPT.format(
                                     language=language,
                                     language_specifics=language_specifics),
                                verify_code=True,
                                test_tool=test_tool,
                                callback=self.display,
                                repository=self.repository)

        logger.info(
            f"Create test suite and implementation for exercise {self.exercise} in {language}")

        message = Message(sender="Human", items=[
            FileItem(file_path="instructions.md"),
            FileItem(file_path=test_file, new=True),
            FileItem(file_path=impl_file, new=True),
        ])

        response_messages = ghostcoder.run(message=message)
        if response_messages[-1].find_items_by_type("verification_failure"):
            self.display.display("Ghostcoder", "Validation failed when trying to create a test suite"
                                               " and implementation based on instructions in `instructions.md` ")
        else:
            found_files = set()
            target_files = {test_file, impl_file}

            for response_message in response_messages:
                for item in response_message.find_items_by_type("updated_file"):
                    if item.file_path in target_files:
                        found_files.add(item.file_path)

            if target_files.issubset(found_files):
                logger.info(f"{found_files} where successfully created..")
            else:
                self.display.display("Failed to create test suite and implementation based on instructions in `instructions.md`.")

    def review_test_suite(self, language: str = "python"):
        self.assert_exercise()
        # TODO: Check for test and implementation files

        llm = self.create_openai_client(llm_name=self.smart_llm_name, temperature=0.0)

        language_dir = self.exercises_dir / self.exercise / language

        language_specifics = ""
        if language == "python":
            language_specifics = CREATE_STUBS_PYTHON_RULES
            test_tool = PythonUnittestTestTool(current_dir=language_dir, callback=self.display)
        elif language == "java":
            language_specifics = CREATE_STUBS_JAVA_RULES
            test_tool = JavaMvnUnit5TestTool(current_dir=language_dir, callback=self.display)

        ghostcoder = Ghostcoder(llm=llm,
                                code_writer_sys_prompt=VERIFY_TEST_SYSTEM_PROMPT.format(language_specifics),
                                callback=self.display,
                                verify_code=True,
                                test_tool=test_tool,
                                repository=self.repository)

        logger.debug(f"Review test suite")

        file_items = self.repository.get_source_files(
            language=language,
            directory=f"{language}",
            include_test_files=True)

        message = Message(sender="Human",
                          items=[FileItem(file_path="instructions.md")] + file_items)

        response_messages = ghostcoder.run(message=message)
        if response_messages[-1].find_items_by_type("verification_failure"):
            display(
                Markdown(f"_The updated tests didn't pass the tests. "
                         f"Call this function again to try again or create a new instruction._"),
                display_id="review_test_suite")

    def create_stubs(self, language: str = "python"):
        self.assert_exercise()
        # TODO: Check for test and implementation files

        def ignore_example(dir, filenames):
            return ['.example']

        language_dir = self.exercise_dir / language
        example_dir = language_dir / ".example"
        example_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(language_dir, example_dir, dirs_exist_ok=True, ignore=ignore_example)

        llm = self.create_openai_client(llm_name="gpt-4", temperature=0.0)

        language_specifics = ""
        if language == "python":
            language_specifics = CREATE_STUBS_PYTHON_RULES
        elif language == "java":
            language_specifics = CREATE_STUBS_JAVA_RULES

        ghostcoder = Ghostcoder(llm=llm,
                                code_writer_sys_prompt=CREATE_STUBS_SYSTEM_PROMPT.format(
                                    language_specifics=language_specifics),
                                callback=self.display,
                                repository=self.repository,
                                max_retries=0)

        instruction_file = f"instructions.md"



        file_items = self.repository.get_source_files(
            language=language,
            directory=f"{language}")

        filepaths = "`, `".join([file_item.file_path for file_item in file_items])
        items = [TextItem(text=f"Replace the code in `{filepaths}`"),
                 FileItem(file_path=instruction_file, readonly=True)]
        items.extend(file_items)

        message = Message(sender="Human", items=items)
        response_messages = ghostcoder.run(message=message) # TODO CREATE_STUBS_FEW_SHOTS +
        response_message = response_messages[-1]

    def run_and_verify_exercise(self, language: str = "python"):
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
                language=language,
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
                    language=language,
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

        instruction_file = f"instructions.md"

        # FIXME: not only python
        test_file = f"{language}/{self.exercise}_test.py"
        impl_file = f"{language}/{self.exercise}.py"
        stub_file = f"{language}/stubs/{self.exercise}.py"
        stub_with_comments = f"{language}/stub_with_comments/{self.exercise}.py"

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

    def create_openai_client(self, llm_name: str, temperature: float, streaming: bool = True):
        callback = LogCallbackHandler(str(self.prompt_log_dir))
        return ChatLLMWrapper(ChatOpenAI(
            model=llm_name,
            temperature=temperature,
            streaming=streaming,
            callbacks=[callback]
        ))

    def get_resource(self, resource_name: str):
        script_dir = Path(__file__).parent
        resource_path = script_dir / "resources" / resource_name
        return resource_path.read_text()

    def create_coder_writer(self,
                            llm: LLMWrapper,
                            sys_prompt: str = None,
                            expect_one_file: bool = False,
                            allow_hallucinated_files: bool = False):
        return CodeWriter(llm=llm,
                          sys_prompt=sys_prompt,
                          repository=self.repository,
                          callback=self.display,
                          auto_mode=True,
                          expect_one_file=expect_one_file,
                          allow_hallucinated_files=allow_hallucinated_files)
