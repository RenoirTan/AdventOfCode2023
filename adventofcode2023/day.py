from dataclasses import dataclass
import re

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution
from adventofcode2023 import d01, d02, d03


@dataclass
class Day(object):
    problem_class: type[Problem]
    solution_class: type[Solution]


DAYS: dict[int, Day] = {
    1: Day(d01.Problem01, d01.Solution01),
    2: Day(d02.Problem02, d02.Solution02),
    3: Day(d03.Problem03, d03.Solution03)
}

DAY_SEARCHER_RE = re.compile(
    pattern=r"d?(?P<n>0*([01]?\d|2[012345]))",
    flags=re.I
)

def search_day(search: str) -> Day:
    m = DAY_SEARCHER_RE.match(search)
    n = m.group("n")
    n = int(n)
    return DAYS[n]