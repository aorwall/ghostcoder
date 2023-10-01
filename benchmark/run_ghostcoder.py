from pathlib import Path

from ghostcoder.benchmark.utils import create_openai_client
from ghostcoder import FileRepository, Ghostcoder
from ghostcoder.schema import Message, TextItem, FileItem, Item
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('openai')
logger.setLevel(logging.INFO)

repo_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark/benchmark-results/2023-09-17-19-59-56--gpt-4/paasio")
log_dir = repo_dir / ".prompt_log"

smart_llm_name = "gpt-4"
llm = create_openai_client(log_dir=log_dir, llm_name="gpt-4", temperature=0.0, streaming=False)

repository = FileRepository(repo_path=repo_dir, use_git=False)
ghostcoder = Ghostcoder(llm=llm, repository=repository, verify_code=True, max_retries=5, auto_mode=True, language="python")

message = Message(sender="Human", items=[
    TextItem(text=repository.get_file_content("/instructions.md")),
    FileItem(file_path="paasio.py")
])

ghostcoder.run(message=message)