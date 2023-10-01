from ghostcoder.benchmark import Benchmark
from ghostcoder.benchmark.utils import create_openai_client, create_testgen_client
from pathlib import Path
import logging

from ghostcoder.sysout_callback import SysoutCallback

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('openai').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)

basic_llm_name = "gpt-3.5-turbo"
smart_llm_name = "gpt-4"
exercises_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark/exercises/exercism-python")

exercise = "bowling"
language = "python"

benchmark_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark")
benchmark_result_dir = benchmark_dir / "benchmark-results"
benchmark_result_dir.mkdir(parents=True, exist_ok=True)
log_dir = benchmark_result_dir / ".prompt_log"

basic_llm = create_openai_client(log_dir=log_dir, llm_name=basic_llm_name, temperature=0.0, streaming=False)
llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0, streaming=False)
smart_llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0, streaming=False)

benchmark = Benchmark(
    llm=llm,
    basic_llm=basic_llm,
    llm_name=smart_llm_name,
    llm_params={"temperature": 0.0},
    exercises_dir=exercises_dir,
    benchmarks_dir=benchmark_result_dir,
    reviewer_llm=smart_llm,
    exercise=exercise,
    language=language,
    callback=None
)

benchmark.run_exercise(exercise=exercise)
