from ghostcoder.create_exercise import ExerciseBuilder
from pathlib import Path
import logging
logging.basicConfig(level=logging.DEBUG)

builder = ExerciseBuilder(
     exercises_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark/exercises/small"),
     benchmark_results_dir = Path("/home/albert/repos/albert/ghostcoder-lite/benchmark/results"),
     exercise = "coffee_machine_program"
)

builder.create_stubs("java")