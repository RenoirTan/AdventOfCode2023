from dataclasses import dataclass, field
from enum import Enum
import math
import typing as t

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass
class PipeDataMixin(object):
    visual: str
    north: bool = field(repr=False, default=False)
    south: bool = field(repr=False, default=False)
    east: bool = field(repr=False, default=False)
    west: bool = field(repr=False, default=False)
    
    @staticmethod
    def nsew(input: int) -> tuple[bool, bool, bool, bool]:
        return bool(input & 8), bool(input & 4), bool(input & 2), bool(input & 1)


def cross_product(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    )


def topology_between(a: tuple[int, int], b: tuple[int, int]) -> int:
    """
    For 2 direction vectors a and b, return the topology value between them.
    If b is 90 degrees clockwise to a, the result is positive.
    If b is 90 degrees anticlockwise to a, the result is negative.
    Otherwise, the result is 0.
    Unlike a normal cross product, clockwise vectors gives a positive result.
    """
    v = cross_product((a[0], a[1], 0), (b[0], b[1], 0))[2]
    return 1 if v > 0 else -1 if v < 0 else 0 # normalised


# https://math.stackexchange.com/a/32602
def inverse_normalized_orthogonal_cross_product(
    c: tuple[int, int, int],
    a: tuple[int, int, int]
) -> tuple[int, int, int]:
    return cross_product(c, a)


def side_of_direction(direction: tuple[int, int], topology: int) -> tuple[int, int]:
    dx, dy = direction
    v = inverse_normalized_orthogonal_cross_product((dx, dy, 0), (0, 0, -topology))
    return v[0], v[1]


class Pipe(PipeDataMixin, Enum):
    Vertical = "|", True, True, False, False
    Horizontal = "-", False, False, True, True
    NorthEast = "L", True, False, True, False
    NorthWest = "J", True, False, False, True
    SouthWest = "7", False, True, False, True
    SouthEast = "F", False, True, True, False
    Ground = ".", False, False, False, False
    Start = "S", True, True, True, True
    
    @classmethod
    def from_str(cls, input: str) -> "Pipe":
        match input:
            case "|": return Pipe.Vertical
            case "-": return Pipe.Horizontal
            case "L": return Pipe.NorthEast
            case "J": return Pipe.NorthWest
            case "7": return Pipe.SouthWest
            case "F": return Pipe.SouthEast
            case ".": return Pipe.Ground
            case "S": return Pipe.Start
        raise ValueError(f"unrecognized pipe: {input}")
    
    def neighbors_of(self, x: int, y: int) -> list[tuple[int, int]]:
        neighbors = []
        if self.north:
            neighbors.append((x, y-1))
        if self.south:
            neighbors.append((x, y+1))
        if self.east:
            neighbors.append((x+1, y))
        if self.west:
            neighbors.append((x-1, y))
        return neighbors
    
    def is_corner(self) -> bool:
        return self.visual in {"L", "J", "7", "F"}


class Problem10(Problem):
    def __init__(self, grid: list[list[Pipe]]):
        self.height = len(grid)
        self.width = len(grid[0])
        self.grid = grid
        for y, line in enumerate(grid):
            for x, pipe in enumerate(line):
                if pipe == Pipe.Start:
                    self.s_coord = x, y
    
    @classmethod
    def from_str(cls, input: str) -> "Problem10":
        grid = [[Pipe.from_str(s) for s in line] for line in input.splitlines()]
        return Problem10(grid)


class Solution10(Solution):
    def get_history(self, problem: Problem10) -> list[tuple[int, int]]:
        sx, sy = problem.s_coord
        x, y = None, None
        
        # check which of the pipes neighbouring start is connected to start
        if sy >= 1 and problem.grid[sy-1][sx].south:
            x, y = sx, sy - 1
        if sy+1 < problem.height and problem.grid[sy+1][sx].north:
            x, y = sx, sy + 1
        if sx+1 < problem.width and problem.grid[sy][sx+1].west:
            x, y = sx + 1, sy
        if sx >= 1 and problem.grid[sy][sx-1].east:
            x, y = sx - 1, sy
        
        if x is None or y is None:
            raise ValueError("start not found")
        
        history: list[tuple[int, int]] = [(sx, sy)]
        
        while True:
            pipe = problem.grid[y][x]
            px, py = history[-1]
            # do not visit previous
            n = next(filter(lambda n: n != (px, py), pipe.neighbors_of(x, y)))
            next_pipe = problem.grid[n[1]][n[0]]
            if next_pipe == Pipe.Ground:
                raise ValueError("wtf")
            history.append((x, y))
            if next_pipe == Pipe.Start:
                history.append(n)
                break
            x, y = n
        return history
    
    def p1(self, problem: Problem10) -> int:
        return int(len(self.get_history(problem)) / 2)
    
    def p2(self, problem: Problem10) -> int:
        history = self.get_history(problem)
        directions = [(b[0] - a[0], b[1] - a[1]) for a, b in zip(history, history[1:])]
        directions[0] = directions[-1] # helpful if the start pipe is a corner
        # positive topology means clockwise, negative means anticlockwise
        # a loop should have non-zero topology
        topology = sum(topology_between(a, b) for a, b in zip(directions, directions[1:]))
        if topology == 0:
            raise ValueError("expected a loop!")
        topology = 1 if topology > 0 else -1 if topology < 0 else 0
        visited: list[list[bool]] = [[False] * problem.width for _ in range(problem.height)]
        for x, y in history:
            visited[y][x] = True
        nest_size = 0
        
        # hx, hy are the coordinates to the current pipe
        # dx, dy are the current direction of travel
        # if the current pipe is a corner, this will be the new direction after
        # the turn induced by the corner
        # pdx, pdy are the original direction of travel, which is only relevant
        # for corner pipes
        # 
        # the reason why the new and previous direction are relevant can be
        # shown by the following diagram
        #
        # .|..
        # -J..
        # ..F-
        #
        # let's say we are trying to mark the "outer" cells, i.e. the 4
        # ground cells in the top right and the 2 ground cells in the bottom
        # left
        # upon reaching 'J' from the vertical pipe down south, we immediately
        # change direction to the west. however, our current setup only allows
        # us to mark the bottom-leftmost 2 ground cells.
        # by considering the previous direction of south, we now know to also
        # mark the 4 ground cells in the top right
        for (hx, hy), (dx, dy), (pdx, pdy) in zip(history[1:], directions[1:], directions):
            dx, dy = side_of_direction((dx, dy), topology)
            dfs: list[tuple[int, int]] = []
            # get side of the path that is "inside"
            x, y = hx + dx, hy + dy
            if not visited[y][x]:
                dfs.append((x, y))
                visited[y][x] = True
            pdx, pdy = side_of_direction((pdx, pdy), topology)
            x, y = hx + pdx, hy + pdy
            if problem.grid[hy][hx].is_corner() and not visited[y][x]:
                dfs.append((x, y))
                visited[y][x] = True
            while len(dfs) >= 1:
                x, y = dfs.pop()
                nest_size += 1
                if y >= 1 and not visited[y-1][x]:
                    dfs.append((x, y-1))
                    visited[y-1][x] = True
                if y+1 < problem.height and not visited[y+1][x]:
                    dfs.append((x, y+1))
                    visited[y+1][x] = True
                if x+1 < problem.width and not visited[y][x+1]:
                    dfs.append((x+1, y))
                    visited[y][x+1] = True
                if x >= 1 and not visited[y][x-1]:
                    dfs.append((x-1, y))
                    visited[y][x-1] = True
        
        # for row in visited:
            # print("".join("I" if v else "." for v in row))
        return nest_size