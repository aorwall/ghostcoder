import logging
from typing import List

from ghostcoder.actions import CodeWriter
from ghostcoder.actions.verify.code_verifier import CodeVerifier
from ghostcoder.actions.write_code.prompt import FIX_TESTS_PROMPT
from ghostcoder.filerepository import FileRepository
from ghostcoder.ipython_callback import DisplayCallback
from ghostcoder.llm import LLMWrapper
from ghostcoder.schema import Message, UpdatedFileItem, TextItem, FileItem
from ghostcoder.test_tools import TestTool

logger = logging.getLogger(__name__)

class Ghostcoder:

    def __init__(self,
                 llm: LLMWrapper,
                 basic_llm: LLMWrapper,
                 repository: FileRepository,
                 code_writer_sys_prompt: str = None,
                 verify_code: bool = False,
                 test_tool: TestTool = None,
                 auto_mode: bool = True,
                 language: str = None,
                 callback: DisplayCallback = None,
                 max_retries: int = 3):
        self.basic_llm = basic_llm
        self.repository = repository
        self.code_writer = CodeWriter(llm=llm,
                                      sys_prompt=code_writer_sys_prompt,
                                      repository=self.repository,
                                      callback=callback,
                                      auto_mode=True)
        self.test_fix_writer = CodeWriter(llm=llm,
                                          sys_prompt=FIX_TESTS_PROMPT,
                                          repository=self.repository,
                                          callback=callback,
                                          auto_mode=True)
        self.max_retries = max_retries
        self.auto_mode = auto_mode
        self.callback = callback

        if verify_code:
            self.verifier = CodeVerifier(repository=self.repository, test_tool=test_tool, language=language, callback=callback)
        else:
            self.verifier = None

    def run(self, message: Message) -> List[Message]:
        file_items = message.find_items_by_type(item_type="file")
        for file_item in file_items:
            if not file_item.content and self.repository:
                logger.debug(f"Get current file content for {file_item.file_path}")
                content = self.repository.get_file_content(file_path=file_item.file_path)
                if content:
                    file_item.content = content
                elif file_item.new:
                    file_item.content = ""
                else:
                    raise Exception(f"File {file_item.file_path} not found in repository.")

        if self.callback:
            self.callback.display_message(message)

        return self._run(message)

    def _run(self, incoming_message: Message) -> List[Message]:
        outgoing_messages = self.code_writer.execute(incoming_messages=[incoming_message])
        outgoing_messages.extend(self.verify(messages=[incoming_message] + outgoing_messages))
        return outgoing_messages

    def verify(self, messages: List[Message], retry: int = 0, last_run: int = 0) -> [Message]:
        if not self.verifier:
            return []

        updated_files = dict()

        for message in messages:
            for item in message.items:
                if isinstance(item, UpdatedFileItem) and not item.invalid:
                    updated_files[item.file_path] = item

        if not updated_files:
            # TODO: Handle if no files where updated in last run?
            return []

        file_items = []
        for file_item in updated_files.values():
            if self.repository:
                content = self.repository.get_file_content(file_path=file_item.file_path)
            else:
                content = file_item.content

            file_items.append(FileItem(file_path=file_item.file_path,
                                       content=content,
                                       invalid=file_item.invalid))

        outgoing_messages = []

        logger.info(f"Updated files, verifying...")
        verification_message = self.verifier.execute()
        if self.callback:
            self.callback.display_message(verification_message)
        outgoing_messages.append(verification_message)

        failures = verification_message.find_items_by_type("verification_failure")
        if failures:
            if retry < self.max_retries or len(failures) < last_run:
                verification_message.items.extend(file_items)

                retry += 1
                incoming_messages = self.make_summary(messages)

                logger.info(f"{len(failures)} verifications failed (last run {last_run}, retrying ({retry}/{self.max_retries})...")
                incoming_messages.append(verification_message)
                response_messages = self.test_fix_writer.execute(incoming_messages=incoming_messages)
                return self.verify(messages=messages + [verification_message] + response_messages,
                                   retry=retry,
                                   last_run=len(failures))
            else:
                logger.info(f"Verification failed, giving up...")

        return outgoing_messages

    def make_summary(self, messages: List[Message]) -> List[Message]:
        summarized_messages = []
        sys_prompt = """Make a short summary of the provided message."""

        for message in messages:
            if message.sender == "Human":
                text_items = message.find_items_by_type("text")
                summarized_messages.append(Message(sender=message.sender, items=text_items))
            else:
                if not message.summary and self.basic_llm:
                    message.summary, stats = self.basic_llm.generate(sys_prompt, messages=[message])
                    logger.debug(f"Created summary {stats.json}")
                if message.summary:
                    summarized_messages.append(Message(sender=message.sender, items=[TextItem(text=message.summary)]))

        return summarized_messages
