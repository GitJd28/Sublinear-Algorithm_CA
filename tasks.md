# Task List

## Project Setup
- [ ] Create project folders: `src/`, `tests/`, `benchmarks/`
- [ ] Add package entrypoint in `src/__init__.py`

## HLL Implementation
- [ ] Implement a MurmurHash3 64-bit hash helper
- [ ] Create `HyperLogLog` with configurable precision `p`
- [ ] Store register values in a compact `bytearray`
- [ ] Compute register index and rank from 64-bit hash
- [ ] Implement `add()` for new elements
- [ ] Implement `estimate()` using the harmonic mean formula
- [ ] Apply small-range correction for low cardinalities
- [ ] Add a `merge()` method for future composability (optional)

## Benchmarking and Comparison
- [ ] Write a benchmark script to generate 1 million random strings
- [ ] Compare HLL estimate against exact count using `set`
- [ ] Calculate and report relative error

## Testing
- [ ] Add tests for empty HLL
- [ ] Add tests for a small known unique dataset
- [ ] Verify relative error stays within acceptable bounds for random data

## Documentation
- [ ] Document requirements in `requirements.md`
- [ ] Document design in `design.md`
- [ ] Document implementation tasks in `tasks.md`
