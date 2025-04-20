"""
```
Let k be the amount of time given for a race,
    r be the distance of the record holder,
    t be the amount of time the button is held,
    s be the actual distance travelled
s = (k-t)(t) = kt - t²
s > r
<=> t² - kt + r < 0
Considering t² - kt + r = 0:
t = (k ± √(k² - 4r)) / 2
```
"""

from dataclasses import dataclass
from functools import reduce
import math

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass
class Race(object):
    time: int
    record_distance: int
    
    @property
    def discriminant(self) -> int:
        return self.time ** 2 - 4 * self.record_distance
    
    def winning_range(self) -> tuple[int, int]:
        common: float = self.time / 2
        divergent: float = (self.discriminant ** 0.5) / 2
        lower = common - divergent
        upper = common + divergent
        lower = math.ceil(lower) + (1 if lower.is_integer() else 0)
        upper = math.ceil(upper)
        return lower, upper
    
    def margin_of_error(self) -> int:
        lower, upper = self.winning_range()
        return upper - lower


class Problem06(Problem):
    def __init__(self, races: list[Race]):
        self.races = races
        self.mega_race = Race(
            int("".join(str(r.time) for r in self.races)),
            int("".join(str(r.record_distance) for r in self.races))
        )
    
    @classmethod
    def from_str(cls, input: str) -> "Problem06":
        lines = input.splitlines()
        times = (int(k) for k in lines[0].split(" ") if k.isdigit())
        record_distances = (int(r) for r in lines[1].split(" ") if r.isdigit())
        races = [Race(k, r) for k, r in zip(times, record_distances)]
        return Problem06(races)


class Solution06(Solution):
    def p1(self, problem: Problem06) -> int:
        return reduce(lambda m, r: m * r.margin_of_error(), problem.races, 1)
    
    def p2(self, problem: Problem06) -> int:
        return problem.mega_race.margin_of_error()