from functools import reduce

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


def column_at(pattern: list[list[bool]], x: int) -> list[bool]:
    return [row[x] for row in pattern]


def transpose(pattern: list[list[bool]]) -> list[list[bool]]:
    return [column_at(pattern, x) for x in range(len(pattern[0]))]


def diff_count(a: list[bool], b: list[bool]) -> int:
    return sum(int(a ^ b) for a, b in zip(a, b))


def diff_total(pattern: list[list[bool]], y: int) -> int:
    i, j = y, y + 1
    height = len(pattern)
    diff_total = 0
    while i >= 0 and j < height:
        diff_total += diff_count(pattern[i], pattern[j])
        i -= 1
        j += 1
    return diff_total


def check_symmetry(pattern: list[list[bool]], y: int, diff: int = 0) -> bool:
    return diff_total(pattern, y) == diff


def get_symmetry(pattern: list[list[bool]], diff: int = 0) -> tuple[int, int]:
    height = len(pattern)
    width = len(pattern[0])
    transposed = transpose(pattern)
    res_x = 0
    for x in range(width - 1):
        if check_symmetry(transposed, x, diff):
            res_x = x + 1
            break
    res_y = 0
    for y in range(height - 1):
        if check_symmetry(pattern, y, diff):
            res_y = y + 1
            break
    return res_x, res_y


def tuple_sum(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(a, b))


class Problem13(Problem):
    def __init__(self, patterns: list[list[list[bool]]]):
        self.patterns = patterns
    
    @classmethod
    def from_str(cls, input: str) -> "Problem13":
        patterns: list[list[list[bool]]] = []
        pattern: list[list[bool]] = []
        for line in input.splitlines():
            if len(line) == 0:
                patterns.append(pattern)
                pattern = []
            else:
                pattern.append([c == "#" for c in line])
        else:
            if len(pattern) >= 1:
                patterns.append(pattern)
        return Problem13(patterns)


class Solution13(Solution):
    def p1(self, problem: Problem13) -> int:
        x, y = reduce(tuple_sum, map(get_symmetry, problem.patterns))
        return x + y * 100
    
    def p2(self, problem: Problem13) -> int:
        x, y = reduce(tuple_sum, map(lambda p: get_symmetry(p, 1), problem.patterns))
        return x + y * 100