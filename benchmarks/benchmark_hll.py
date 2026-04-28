import random
import string
import time

from src.hll import HyperLogLog


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _prompt_int(prompt: str, default: int, min_value: int = 1) -> int:
    while True:
        response = input(f"{prompt} [{default}]: ").strip()
        if not response:
            return default
        if response.isdigit():
            value = int(response)
            if value >= min_value:
                return value
        print(f"Please enter an integer >= {min_value}.")


def main() -> None:
    sample_size = _prompt_int("Enter number of stream elements", 1_000_000, 1)
    precision = _prompt_int("Enter HLL precision (p)", 12, 4)
    hll = HyperLogLog(precision=precision)
    exact_values = set()

    start = time.perf_counter()
    for _ in range(sample_size):
        value = random_string(12)
        exact_values.add(value)
        hll.add(value)
    end = time.perf_counter()

    exact_count = len(exact_values)
    estimate = hll.estimate()
    relative_error = abs(estimate - exact_count) / exact_count if exact_count else 0.0

    print(f"Sample size: {sample_size}")
    print(f"Exact unique count: {exact_count}")
    print(f"HLL precision: {precision} (registers={hll.num_registers})")
    print(f"HLL estimate: {estimate:.2f}")
    print(f"Relative error: {relative_error * 100:.3f}%")
    print(f"Duration: {end - start:.2f} seconds")


if __name__ == "__main__":
    main()
