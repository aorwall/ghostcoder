from ghostcoder.benchmark import Benchmark
from ghostcoder.benchmark.utils import create_openai_client, create_testgen_client
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

basic_llm_name = "gpt-3.5-turbo"
smart_llm_name = "gpt-4"
exercises_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark/exercises/one_file")

exercise = "real_estate_concurrent_processing"

benchmark_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark")
benchmark_result_dir = benchmark_dir / "test_results"
benchmark_result_dir.mkdir(parents=True, exist_ok=True)
log_dir = benchmark_result_dir / "prompt_log"

llm = create_testgen_client(log_dir=log_dir, llm_name=basic_llm_name, temperature=0.0)
smart_llm = create_openai_client(log_dir=log_dir, llm_name=smart_llm_name, temperature=0.0)

benchmark = Benchmark(
    llm=llm,
    llm_name=basic_llm_name,
    llm_params={"temperature": 0.0},
    exercises_dir=exercises_dir,
    benchmarks_dir=benchmark_result_dir,
    reviewer_llm=smart_llm
)

benchmark.run_exercise(exercise=exercise)
