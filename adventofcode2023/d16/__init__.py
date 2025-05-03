from dataclasses import dataclass
from enum import Enum
import operator
import typing as t

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass(unsafe_hash=True)
class Vector(object):
    x: int
    y: int
    
    def splat(self) -> tuple[int, int]:
        return self.x, self.y
    
    def apply_ortho(self, func: t.Callable[[int, int], int], other: "Vector") -> "Vector":
        return Vector(func(self.x, other.x), func(self.y, other.y))
    
    def __add__(self, other: "Vector") -> "Vector":
        return self.apply_ortho(operator.add, other)
    
    def __sub__(self, other: "Vector") -> "Vector":
        return self.apply_ortho(operator.sub, other)
    
    def __matmul__(self, other: "Vector") -> int:
        return self.x * other.x + self.y * other.y


class Direction(Vector, Enum):
    UP = 0, -1
    DOWN = 0, 1
    LEFT = -1, 0
    RIGHT = 1, 0


class Tile(Enum):
    EMPTY = "."
    FRONT_MIRROR = "/"
    BACK_MIRROR = "\\"
    VERTICAL_SPLITTER = "|"
    HORIZONTAL_SPLITTER = "-"
    
    def passthrough_light(self, direction: Direction) -> list[Direction]:
        return PASSTHROUGH[self, direction]


FRONT_MIRROR = [
    (Direction.UP, Direction.RIGHT), (Direction.RIGHT, Direction.UP),
    (Direction.DOWN, Direction.LEFT), (Direction.LEFT, Direction.DOWN)
]
BACK_MIRROR = [
    (Direction.UP, Direction.LEFT), (Direction.LEFT, Direction.UP),
    (Direction.DOWN, Direction.RIGHT), (Direction.RIGHT, Direction.DOWN)
]
PASSTHROUGH: dict[tuple[Tile, Direction], list[Direction]] = (
    {(Tile.EMPTY, direction): [direction] for direction in Direction}
    | {(Tile.FRONT_MIRROR, a): [b] for a, b in FRONT_MIRROR}
    | {(Tile.BACK_MIRROR, a): [b] for a, b in BACK_MIRROR}
    | {
        (Tile.VERTICAL_SPLITTER, Direction.UP): [Direction.UP],
        (Tile.VERTICAL_SPLITTER, Direction.DOWN): [Direction.DOWN],
        (Tile.VERTICAL_SPLITTER, Direction.LEFT): [Direction.UP, Direction.DOWN],
        (Tile.VERTICAL_SPLITTER, Direction.RIGHT): [Direction.UP, Direction.DOWN],
        (Tile.HORIZONTAL_SPLITTER, Direction.LEFT): [Direction.LEFT],
        (Tile.HORIZONTAL_SPLITTER, Direction.RIGHT): [Direction.RIGHT],
        (Tile.HORIZONTAL_SPLITTER, Direction.UP): [Direction.LEFT, Direction.RIGHT],
        (Tile.HORIZONTAL_SPLITTER, Direction.DOWN): [Direction.LEFT, Direction.RIGHT]
    }
)


@dataclass
class TileState(object):
    tile: Tile
    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0

    def reset(self) -> "TileState":
        self.up = 0
        self.down = 0
        self.left = 0
        self.right = 0
        return self
    
    def visited(self, direction: Direction) -> bool:
        match direction:
            case Direction.UP: return self.up >= 1
            case Direction.DOWN: return self.down >= 1
            case Direction.LEFT: return self.left >= 1
            case Direction.RIGHT: return self.right >= 1
    
    def visited_any(self) -> bool:
        return (self.up + self.down + self.left + self.right) >= 1
    
    def visit(self, direction: Direction) -> bool:
        match direction:
            case Direction.UP: self.up += 1
            case Direction.DOWN: self.down += 1
            case Direction.LEFT: self.left += 1
            case Direction.RIGHT: self.right += 1


@dataclass
class StatefulLayout(object):
    m: list[list[TileState]]
    
    @classmethod
    def from_layout(cls, layout: list[list[Tile]]) -> "StatefulLayout":
        return StatefulLayout([[TileState(tile) for tile in row] for row in layout])
    
    def reset(self) -> "StatefulLayout":
        for row in self.m:
            for tile in row:
                tile.reset()
    
    def count_visited(self) -> int:
        return sum(sum(int(t.visited_any()) for t in row) for row in self.m)


class Problem16(Problem):
    def __init__(self, layout: list[list[Tile]]):
        self.layout = layout
        self.height = len(layout)
        self.width = len(layout)
    
    @classmethod
    def from_str(cls, input: str) -> "Problem16":
        layout = [[Tile(c) for c in line] for line in input.splitlines()]
        return Problem16(layout)


class Solution16(Solution):
    def p1(
        self,
        problem: Problem16,
        initial_vector: Vector = Vector(0, 0),
        initial_direction: Direction = Direction.RIGHT
    ) -> int:
        tiles = StatefulLayout.from_layout(problem.layout)
        dfs: list[tuple[Vector, Direction]] = [(initial_vector, initial_direction)]
        while len(dfs) >= 1:
            vector, direction = dfs.pop()
            x, y = vector.splat()
            tile = tiles.m[y][x]
            if tile.visited(direction):
                continue
            tile.visit(direction)
            directions = tile.tile.passthrough_light(direction)
            for d in directions:
                nx, ny = x + d.x, y + d.y
                if nx < 0 or nx >= problem.width or ny < 0 or ny >= problem.height:
                    continue
                dfs.append((Vector(nx, ny), d))
        return tiles.count_visited()
    
    def p2(self, problem: Problem16) -> int:
        e = max(self.p1(problem, Vector(x, 0), Direction.DOWN) for x in range(problem.width))
        e = max(e, *(
            self.p1(problem, Vector(x, problem.height - 1), Direction.UP)
            for x in range(problem.width)
        ))
        e = max(e, *(
            self.p1(problem, Vector(0, y), Direction.RIGHT)
            for y in range(problem.height)
        ))
        e = max(e, *(
            self.p1(problem, Vector(problem.width - 1, y), Direction.LEFT)
            for y in range(problem.height)
        ))
        return e