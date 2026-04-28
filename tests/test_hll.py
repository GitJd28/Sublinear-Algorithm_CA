import random
import string

from src.hll import HyperLogLog


def random_string(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def test_empty_hll_estimate_is_zero() -> None:
    hll = HyperLogLog(precision=10)
    assert hll.estimate() == 0.0


def test_hll_estimate_for_small_unique_collection() -> None:
    values = [f"item-{i}" for i in range(2000)]
    hll = HyperLogLog(precision=12)
    hll.update(values)

    estimate = hll.estimate()
    relative_error = abs(estimate - len(values)) / len(values)
    assert relative_error < 0.15


def test_hll_produces_reasonable_error_on_random_data() -> None:
    values = {random_string(12) for _ in range(10000)}
    hll = HyperLogLog(precision=12)

    for value in values:
        hll.add(value)

    estimate = hll.estimate()
    relative_error = abs(estimate - len(values)) / len(values)
    assert relative_error < 0.15
