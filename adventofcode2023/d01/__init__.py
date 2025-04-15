from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


VERBOSE_DIGITS: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9
} | {str(d): d for d in range(10)}

VD_KEYS = set(VERBOSE_DIGITS.keys())
VD_REVERSED = {k[::-1] for k in VD_KEYS}


class Problem01(Problem):
    def __init__(self, vandalized: list[str]):
        self.vandalized: list[str] = vandalized
    
    @classmethod
    def from_str(cls, input: str) -> "Problem01":
        return Problem01(input.splitlines())


class Solution01(Solution):
    def p1(self, problem: Problem01) -> int:
        return sum((p1_indiv(v) for v in problem.vandalized))
    
    def p2(self, problem: Problem01) -> int:
        return sum((p2_indiv(v) for v in problem.vandalized))


def p1_indiv(vandalized: str) -> int:
    first = int(next(c for c in vandalized if c.isdigit()))
    last = int(next(c for c in vandalized[::-1] if c.isdigit()))
    return first * 10 + last


def p2_indiv(vandalized: str) -> int:
    vand_rev = vandalized[::-1]
    idx = lambda t: t[1]
    # find first appearance of substring in string
    first = min(((k, i) for k in VD_KEYS if (i := vandalized.find(k)) != -1), key=idx)
    last = min(((r[::-1], i) for r in VD_REVERSED if (i := vand_rev.find(r)) != -1), key=idx)
    return VERBOSE_DIGITS[first[0]] * 10 + VERBOSE_DIGITS[last[0]]