import typing as t


from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


class Problem03(Problem):
    def __init__(self, schematic: list[str]):
        self.schematic = schematic
        self.height = len(schematic)
        self.width = len(schematic[0])
    
    @classmethod
    def from_str(cls, input: str) -> "Problem03":
        return Problem03(schematic=input.splitlines())
    
    def get_symbols(self) -> t.Generator[tuple[int, int]]:
        for y in range(self.height):
            for x in range(self.width):
                cell = self.schematic[y][x]
                if not cell.isdigit() and cell != ".":
                    yield x, y
    
    def get_adjacent_cells_of(self, x: int, y: int) -> t.Generator[tuple[int, int]]:
        def inner() -> t.Generator[tuple[int, int]]:
            yield x - 1, y - 1
            yield x, y - 1
            yield x + 1, y - 1
            yield x - 1, y
            yield x + 1, y
            yield x - 1, y + 1
            yield x, y + 1
            yield x + 1, y + 1
        return ((x, y) for x, y in inner() if self.coordinates_exist(x, y))
    
    def coordinates_exist(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height


class Solution03(Solution):
    def __init__(self):
        self.visited: set[tuple[int, int]] = set()
    
    def get_leftmost_digit(
        self,
        problem: Problem03,
        x: int,
        y: int,
        ignore_visited: bool = True
    ) -> tuple[int, int] | None:
        if not problem.schematic[y][x].isdigit():
            return None
        while x >= 0:
            if not problem.schematic[y][x].isdigit():
                if (x + 1, y) in self.visited and ignore_visited:
                    return None
                else:
                    return (x + 1, y)
            x -= 1
        return 0, y
    
    def visit_number(self, problem: Problem03, x: int, y: int) -> int:
        number = 0
        while problem.coordinates_exist(x, y) and (cell := problem.schematic[y][x]).isdigit():
            number = number * 10 + int(cell)
            self.visited.add((x, y))
            x += 1
        return number
    
    def p1(self, problem: Problem03) -> int:
        total = 0
        for x, y in problem.get_symbols():
            for ax, ay in problem.get_adjacent_cells_of(x, y):
                val = self.get_leftmost_digit(problem, ax, ay, True)
                if not val:
                    continue
                lx, ly = val
                number = self.visit_number(problem, lx, ly)
                total += number
        return total
    
    def p2(self, problem: Problem03) -> int:
        total = 0
        for x, y in problem.get_symbols():
            self.visited.clear()
            if problem.schematic[y][x] != "*":
                continue
            adjacents: list[int] = []
            for ax, ay in problem.get_adjacent_cells_of(x, y):
                val = self.get_leftmost_digit(problem, ax, ay, True)
                if not val:
                    continue
                lx, ly = val
                number = self.visit_number(problem, lx, ly)
                adjacents.append(number)
            if len(adjacents) != 2:
                continue
            total += adjacents[0] * adjacents[1]
        return total