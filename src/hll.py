import hashlib
import math
from typing import Iterable, Optional, Union


def _rotl64(x: int, r: int) -> int:
    return ((x << r) & 0xFFFFFFFFFFFFFFFF) | (x >> (64 - r))


def _fmix64(k: int) -> int:
    k ^= k >> 33
    k = (k * 0xff51afd7ed558ccd) & 0xFFFFFFFFFFFFFFFF
    k ^= k >> 33
    k = (k * 0xc4ceb9fe1a85ec53) & 0xFFFFFFFFFFFFFFFF
    k ^= k >> 33
    return k


def murmurhash3_x64_128(key: bytes, seed: int = 0) -> int:
    """Return a stable 64-bit hash from MurmurHash3 x64_128."""
    data = bytearray(key)
    length = len(data)
    nblocks = length // 16

    h1 = seed & 0xFFFFFFFFFFFFFFFF
    h2 = seed & 0xFFFFFFFFFFFFFFFF

    c1 = 0x87c37b91114253d5
    c2 = 0x4cf5ad432745937f

    for block_start in range(0, nblocks * 16, 16):
        k1 = int.from_bytes(data[block_start:block_start + 8], "little")
        k2 = int.from_bytes(data[block_start + 8:block_start + 16], "little")

        k1 = (k1 * c1) & 0xFFFFFFFFFFFFFFFF
        k1 = _rotl64(k1, 31)
        k1 = (k1 * c2) & 0xFFFFFFFFFFFFFFFF
        h1 ^= k1

        h1 = _rotl64(h1, 27)
        h1 = (h1 + h2) & 0xFFFFFFFFFFFFFFFF
        h1 = (h1 * 5 + 0x52dce729) & 0xFFFFFFFFFFFFFFFF

        k2 = (k2 * c2) & 0xFFFFFFFFFFFFFFFF
        k2 = _rotl64(k2, 33)
        k2 = (k2 * c1) & 0xFFFFFFFFFFFFFFFF
        h2 ^= k2

        h2 = _rotl64(h2, 31)
        h2 = (h2 + h1) & 0xFFFFFFFFFFFFFFFF
        h2 = (h2 * 5 + 0x38495ab5) & 0xFFFFFFFFFFFFFFFF

    tail_index = nblocks * 16
    k1 = 0
    k2 = 0
    tail = data[tail_index:]

    if len(tail) >= 15:
        k2 ^= tail[14] << 48
    if len(tail) >= 14:
        k2 ^= tail[13] << 40
    if len(tail) >= 13:
        k2 ^= tail[12] << 32
    if len(tail) >= 12:
        k2 ^= tail[11] << 24
    if len(tail) >= 11:
        k2 ^= tail[10] << 16
    if len(tail) >= 10:
        k2 ^= tail[9] << 8
    if len(tail) >= 9:
        k2 ^= tail[8]

    if len(tail) >= 9:
        k2 = (k2 * c2) & 0xFFFFFFFFFFFFFFFF
        k2 = _rotl64(k2, 33)
        k2 = (k2 * c1) & 0xFFFFFFFFFFFFFFFF
        h2 ^= k2

    if len(tail) >= 8:
        k1 ^= tail[7] << 56
    if len(tail) >= 7:
        k1 ^= tail[6] << 48
    if len(tail) >= 6:
        k1 ^= tail[5] << 40
    if len(tail) >= 5:
        k1 ^= tail[4] << 32
    if len(tail) >= 4:
        k1 ^= tail[3] << 24
    if len(tail) >= 3:
        k1 ^= tail[2] << 16
    if len(tail) >= 2:
        k1 ^= tail[1] << 8
    if len(tail) >= 1:
        k1 ^= tail[0]

    if len(tail) >= 1:
        k1 = (k1 * c1) & 0xFFFFFFFFFFFFFFFF
        k1 = _rotl64(k1, 31)
        k1 = (k1 * c2) & 0xFFFFFFFFFFFFFFFF
        h1 ^= k1

    h1 ^= length
    h2 ^= length

    h1 = (h1 + h2) & 0xFFFFFFFFFFFFFFFF
    h2 = (h2 + h1) & 0xFFFFFFFFFFFFFFFF

    h1 = _fmix64(h1)
    h2 = _fmix64(h2)

    h1 = (h1 + h2) & 0xFFFFFFFFFFFFFFFF
    return h1


class HyperLogLog:
    """HyperLogLog cardinality estimator."""

    def __init__(self, precision: int = 14) -> None:
        if precision < 4 or precision > 18:
            raise ValueError("Precision must be between 4 and 18")
        self.precision = precision
        self.num_registers = 1 << precision
        self.registers = bytearray(self.num_registers)

    def _hash(self, value: Union[str, bytes, int]) -> int:
        if isinstance(value, int):
            value = str(value).encode("utf-8")
        elif isinstance(value, str):
            value = value.encode("utf-8")
        return murmurhash3_x64_128(value)

    def _register_index_and_rank(self, hash_value: int) -> tuple[int, int]:
        index_mask = self.num_registers - 1
        index = hash_value & index_mask
        remaining = hash_value >> self.precision
        rank = self._count_leading_zeros(remaining, 64 - self.precision) + 1
        return index, rank

    @staticmethod
    def _count_leading_zeros(value: int, width: int) -> int:
        if value == 0:
            return width
        return width - value.bit_length()

    def add(self, value: Union[str, bytes, int]) -> None:
        hash_value = self._hash(value)
        index, rank = self._register_index_and_rank(hash_value)
        if rank > self.registers[index]:
            self.registers[index] = rank

    def update(self, values: Iterable[Union[str, bytes, int]]) -> None:
        for value in values:
            self.add(value)

    def _alpha(self) -> float:
        m = self.num_registers
        if m == 16:
            return 0.673
        if m == 32:
            return 0.697
        if m == 64:
            return 0.709
        return 0.7213 / (1 + 1.079 / m)

    def estimate(self) -> float:
        m = self.num_registers
        indicator = 0.0
        zero_count = 0

        for register in self.registers:
            indicator += 2.0 ** -register
            if register == 0:
                zero_count += 1

        raw_estimate = self._alpha() * m * m / indicator

        if raw_estimate <= 5.0 / 2.0 * m and zero_count > 0:
            linear_count = m * math.log(m / zero_count)
            return linear_count

        if raw_estimate > (1 << 64) / 30.0:
            return -((1 << 64) * math.log(1.0 - raw_estimate / (1 << 64)))

        return raw_estimate

    def __len__(self) -> int:
        return int(round(self.estimate()))

    def merge(self, other: "HyperLogLog") -> None:
        if self.precision != other.precision:
            raise ValueError("HyperLogLog instances must have the same precision to merge")
        for i in range(self.num_registers):
            if other.registers[i] > self.registers[i]:
                self.registers[i] = other.registers[i]

    def __repr__(self) -> str:
        return f"HyperLogLog(precision={self.precision}, registers={self.num_registers})"
