from dataclasses import dataclass
from enum import Enum

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass(unsafe_hash=True)
class Vector(object):
    x: int
    y: int
    
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)


@dataclass(unsafe_hash=True)
class DirectionMixin(Vector):
    s: str


class Direction(DirectionMixin, Enum):
    UP = 0, -1, "^"
    DOWN = 0, 1, "v"
    LEFT = -1, 0, "<"
    RIGHT = 1, 0, ">"


class Problem21(Problem):
    def __init__(self, garden: list[str]):
        self.height = len(garden)
        self.width = len(garden[0])
        start = 0, 0
        for y in range(self.height):
            for x in range(self.width):
                if garden[y][x] == "S":
                    start = x, y
        x, y = start
        garden[y] = garden[y][:x] + "." + garden[y][x+1:]
        self.garden = garden
        self.start = Vector(x, y)
    
    @classmethod
    def from_str(cls, input: str) -> "Problem21":
        return Problem21(input.splitlines())
    
    def is_valid_coord(self, v: Vector) -> bool:
        x, y = v.x, v.y
        return 0 <= x < self.width and 0 <= y < self.height


class Solution21(Solution):
    def visit(self, problem: Problem21, max_steps: int | None = None) -> dict[Vector, int]:
        max_steps = max_steps or max(problem.height, problem.width)
        visits: dict[Vector, int] = {problem.start: 0}
        frontier: set[Vector] = {problem.start}
        i = 1
        while i <= max_steps and len(frontier) >= 1:
            new_frontier = set[Vector]()
            for v in frontier:
                for d in Direction:
                    n = v + d
                    if (
                        problem.is_valid_coord(n)
                        and n not in visits
                        and problem.garden[n.y][n.x] == "."
                    ):
                        new_frontier.add(n)
            frontier = new_frontier
            visits |= {v: i for v in new_frontier}
            i += 1
        return visits
    
    def p1(self, problem: Problem21, steps: int = 64) -> int:
        return len(list(v for v in self.visit(problem, steps).values() if v % 2 == steps % 2))
    
    # https://github.com/villuna/aoc23/wiki/A-Geometric-solution-to-advent-of-code-2023,-day-21
    # 26501365 = 65 + (202300 * 131) where n = 202300
    def p2(self, problem: Problem21) -> int:
        visited = self.visit(problem)
        even_cells = len(list(v for v in visited.values() if v % 2 == 0))
        odd_cells = len(list(v for v in visited.values() if v % 2 == 1))
        corner_even_cells = len(list(v for v in visited.values() if v % 2 == 0 and v > 65))
        corner_odd_cells = len(list(v for v in visited.values() if v % 2 == 1 and v > 65))
        n = 202300
        return (
            ((n + 1) ** 2) * odd_cells
            + (n ** 2) * even_cells
            - (n + 1) * corner_odd_cells
            + n * corner_even_cells
        )