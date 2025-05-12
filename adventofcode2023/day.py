from dataclasses import dataclass
import re

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution
from adventofcode2023 import (
    d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11, d12, d13, d14, d15, d16, d17, d18, d19,
    d20, d21, d22
)


@dataclass
class Day(object):
    problem_class: type[Problem]
    solution_class: type[Solution]


DAYS: dict[int, Day] = {
    1: Day(d01.Problem01, d01.Solution01),
    2: Day(d02.Problem02, d02.Solution02),
    3: Day(d03.Problem03, d03.Solution03),
    4: Day(d04.Problem04, d04.Solution04),
    5: Day(d05.Problem05, d05.Solution05),
    6: Day(d06.Problem06, d06.Solution06),
    7: Day(d07.Problem07, d07.Solution07),
    8: Day(d08.Problem08, d08.Solution08),
    9: Day(d09.Problem09, d09.Solution09),
    10: Day(d10.Problem10, d10.Solution10),
    11: Day(d11.Problem11, d11.Solution11),
    12: Day(d12.Problem12, d12.Solution12),
    13: Day(d13.Problem13, d13.Solution13),
    14: Day(d14.Problem14, d14.Solution14),
    15: Day(d15.Problem15, d15.Solution15),
    16: Day(d16.Problem16, d16.Solution16),
    17: Day(d17.Problem17, d17.Solution17),
    18: Day(d18.Problem18, d18.Solution18),
    19: Day(d19.Problem19, d19.Solution19),
    20: Day(d20.Problem20, d20.Solution20),
    21: Day(d21.Problem21, d21.Solution21),
    22: Day(d22.Problem22, d22.Solution22)
}

DAY_SEARCHER_RE = re.compile(
    pattern=r"d?(?P<n>0*[012]?\d)",
    flags=re.I
)

def search_day(search: str) -> Day:
    m = DAY_SEARCHER_RE.match(search)
    n = m.group("n")
    n = int(n)
    return DAYS[n]