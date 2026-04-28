# Project Requirements

## Goal
Build a Python HyperLogLog (HLL) cardinality estimator that approximates the number of unique elements in a massive stream using sublinear memory.

## Functional Requirements
- Implement an `HyperLogLog` class in `src/hll.py`.
- Use a 64-bit hash function for uniform distribution.
  - Preferred: MurmurHash3 64-bit.
- Support configurable precision via `p` registers.
  - The number of registers should be `m = 2**p`.
- Use the Harmonic Mean formula for the final cardinality estimate.
- Provide an exact comparison module using a Python `set` to compute ground truth.
- Include a benchmarking script that:
  - generates a stream of 1 million random strings
  - computes exact unique counts with a `set`
  - computes the HLL estimate
  - reports relative error

## Non-functional Requirements
- Keep memory usage sublinear with respect to the stream size.
- Use readable, idiomatic Python.
- Organize code under `src/` and tests under `tests/`.
- Use standard library dependencies only.

## Deliverables
- `requirements.md`
- `design.md`
- `tasks.md`
- `src/hll.py`
- `src/__init__.py`
- `tests/test_hll.py`
- `benchmarks/benchmark_hll.py`
