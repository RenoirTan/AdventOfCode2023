from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


class Problem11(Problem):
    def __init__(self, points: list[tuple[int, int]], width: int, height: int):
        self.points = points
        self.width = width
        self.height = height
    
    @classmethod
    def from_str(cls, input: str) -> "Problem11":
        points: list[tuple[int, int]] = []
        for y, line in enumerate(input.splitlines()):
            for x, cell in enumerate(line):
                if cell == "#":
                    points.append((x, y))
        width = max(points, key=lambda p: p[0])[0] + 1
        height = max(points, key=lambda p: p[1])[1] + 1
        return Problem11(points, width, height)


class Solution11(Solution):
    def p1(self, problem: Problem11, expansion_factor: int = 2) -> int:
        expansion_factor -= 1 # for part 2
        empty_columns = sorted(set(range(problem.width)) - {x for x, _ in problem.points})
        empty_rows = sorted(set(range(problem.height)) - {y for _, y in problem.points})
        expanded_points = problem.points.copy()
        n = len(problem.points)
        i = 0 # index for empty row/column lists, also size of offset for that point
        # points that have encountered more empty rows/columns should have a larger offset
        expanded_points.sort(key=lambda p: p[0]) # sort by column (x) first
        for j in range(n):
            x, y = expanded_points[j]
            while i < len(empty_columns) and x > empty_columns[i]:
                i += 1
            expanded_points[j] = x + i * expansion_factor, y
        i = 0
        expanded_points.sort(key=lambda p: p[1]) # sort by row (y) next
        for j in range(n):
            x, y = expanded_points[j]
            while i < len(empty_rows) and y > empty_rows[i]:
                i += 1
            expanded_points[j] = x, y + i * expansion_factor
        total = 0
        for i in range(n):
            ax, ay = expanded_points[i]
            for j in range(i + 1, n):
                bx, by = expanded_points[j]
                total += abs(ax - bx) + abs(ay - by)
        return total
    
    def p2(self, problem: Problem11) -> int:
        return self.p1(problem, expansion_factor = 1000000)