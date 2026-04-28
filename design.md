# Design Document

## Overview
The HyperLogLog (HLL) algorithm estimates the cardinality of a data stream using fixed-size registers and probabilistic hashing. It achieves sublinear memory usage by summarizing element hashes rather than storing raw elements.

## Architecture
- `src/hll.py`
  - `HyperLogLog` class
  - `murmurhash3_x64_128` helper function
  - Register array stored as `bytearray`
- `benchmarks/benchmark_hll.py`
  - Generates 1 million random strings
  - Computes exact unique count with `set`
  - Compares against HLL estimate
- `tests/test_hll.py`
  - Unit tests validating estimate quality and edge cases

## Key Components
### 64-bit Hashing
- Use MurmurHash3 x64_128 to produce a stable 64-bit hash.
- Hash uniformity ensures the register selection and rank calculation are unbiased.

### Precision and Registers
- Precision `p` controls the number of registers: `m = 2**p`.
- Each register stores the maximum observed run of leading zeros in the hashed value suffix.
- Using `p` allows users to trade memory for accuracy.

### Harmonic Mean Estimation
- Estimate cardinality using the harmonic mean of register states:

  `E = alpha_m * m**2 / sum(2**-register[i])`

- Constants:
  - `alpha_m` depends on `m`.
- Apply small-range correction using linear counting when many registers are zero.
- Use large-cardinality correction when the raw estimate grows beyond `2**64 / 30`.

## Data Flow
1. Convert input values to bytes.
2. Hash each element into a 64-bit value.
3. Split the hash into:
   - index bits: selects a register
   - remaining bits: used to compute the leading zero count
4. Update the corresponding register to the maximum rank.
5. Compute the cardinality estimate from register values.

## Memory Budget
- `m = 2**p` registers, each 1 byte.
- Example: `p = 11` uses 2048 bytes (~2 KB).
- The design supports `p` values that keep memory around the 1-2 KB range while maintaining strong estimation behavior for large streams.
