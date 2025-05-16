from dataclasses import dataclass, field
from enum import Enum
import typing as t

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
    
    def to_tile(self) -> "Tile":
        return Tile(self.s)


class Tile(Enum):
    PATH = "."
    FOREST = "#"
    UP_SLOPE = "^"
    DOWN_SLOPE = "v"
    LEFT_SLOPE = "<"
    RIGHT_SLOPE = ">"
    
    def to_slope(self) -> Direction | None:
        match self:
            case Tile.UP_SLOPE: return Direction.UP
            case Tile.DOWN_SLOPE: return Direction.DOWN
            case Tile.LEFT_SLOPE: return Direction.LEFT
            case Tile.RIGHT_SLOPE: return Direction.RIGHT
            case _: return None
    
    def to_p2(self) -> "Tile":
        match self:
            case Tile.FOREST: return self
            case _: return Tile.PATH


@dataclass
class Park(object):
    tiles: list[list[Tile]]
    height: int = field(init=False)
    width: int = field(init=False)
    junctions: set[Vector] = field(init=False)
    neighbors_cache: dict[Vector, list[Vector]] = field(init=False, default_factory=dict)
    neighboring_junctions_cache: dict[Vector, dict[Vector, set[Vector]]] = field(
        init=False,
        default_factory=dict
    )
    
    def __post_init__(self):
        self.height = len(self.tiles)
        self.width = len(self.tiles[0])
        
        self.junctions = set[Vector]()
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == Tile.FOREST:
                    continue
                v = Vector(x, y)
                ways = sum(self.is_valid_tile(v + d) for d in Direction)
                if ways != 2:
                    self.junctions.add(v)
    
    @property
    def start(self) -> Vector:
        return Vector(1, 0)
    
    @property
    def end(self) -> Vector:
        return Vector(self.width - 2, self.height - 1)
    
    @classmethod
    def from_str(cls, input: str) -> "Park":
        return Park([[Tile(c) for c in line] for line in input.splitlines()])
    
    def to_p2(self) -> "Park":
        return Park([[t.to_p2() for t in row] for row in self.tiles])
    
    def is_valid_coord(self, v: Vector) -> bool:
        return 0 <= v.x < self.width and 0 <= v.y < self.height
    
    def is_valid_tile(self, v: Vector) -> bool:
        return self.is_valid_coord(v) and self.tiles[v.y][v.x] != Tile.FOREST
    
    def iter_valid_coords(self) -> t.Generator[Vector]:
        return (Vector(x, y) for x in range(self.width) for y in range(self.height))
    
    def iter_valid_tiles(self) -> t.Generator[Vector]:
        return (v for v in self.iter_valid_coords() if self.is_valid_tile(v))
    
    def neighbors_of(self, v: Vector) -> list[Vector]:
        if v in self.neighbors_cache:
            return self.neighbors_cache[v]
        match self.tiles[v.y][v.x]:
            case Tile.FOREST: ns = []
            case Tile.PATH: ns = [w for d in Direction if self.is_valid_tile(w := v + d)]
            case tile:
                d = tile.to_slope()
                assert d is not None
                w = v + d
                ns = [w] if self.is_valid_tile(w) else []
        self.neighbors_cache[v] = ns
        return ns
    
    def neighbors_of_excluding(self, v: Vector, exclude: set[Vector]) -> list[Vector]:
        return [v for v in self.neighbors_of(v) if v not in exclude]
    
    def neighboring_junctions_of(self, v: Vector) -> dict[Vector, set[Vector]]:
        if v in self.neighboring_junctions_cache:
            return self.neighboring_junctions_cache[v]
        result = dict[Vector, set[Vector]]()
        hikes = [Hike(self, {v}, n) for n in self.neighbors_of(v)]
        while len(hikes) >= 1:
            hike = hikes.pop(0)
            if hike.current in self.junctions:
                result[hike.current] = hike.visited
                continue
            next_hikes = hike.next_hikes()
            assert len(next_hikes) <= 1
            if len(next_hikes) == 0:
                result[hike.current] = hike.visited
                continue
            else:
                hikes.append(next_hikes[0])
        self.neighboring_junctions_cache[v] = result
        return result


@dataclass
class Hike(object):
    park: Park
    visited: set[Vector]
    current: Vector
    
    def __len__(self) -> int:
        return len(self.visited)
    
    def __eq__(self, other: "Hike") -> bool:
        return self.visited == other.visited and self.current == other.current
    
    def __hash__(self) -> int:
        return hash((tuple(self.visited), self.current))
    
    def is_at_end(self) -> bool:
        return self.current == self.park.end
    
    def next_hikes(self) -> list["Hike"]:
        if self.is_at_end():
            return []
        neighbors = self.park.neighbors_of_excluding(self.current, self.visited)
        return [Hike(self.park, self.visited | {self.current}, n) for n in neighbors]
    
    def next_junctions_hikes(self) -> list["Hike"]:
        if self.is_at_end():
            return []
        neighboring_junctions = self.park.neighboring_junctions_of(self.current)
        next_hikes = list["Hike"]()
        for junction, visited in neighboring_junctions:
            if len(visited & self.visited) >= 1:
                continue
            next_hikes.append(Hike(self.park, visited | self.visited, junction))
        return next_hikes


@dataclass
class JunctionHike(object):
    graph: dict[Vector, dict[Vector, int]] = field(repr=False)
    visited: set[Vector]
    current: Vector
    distance: int = 0
    
    def __hash__(self) -> int:
        return hash((tuple(self.visited), self.current, self.distance))
    
    def __eq__(self, other: "JunctionHike") -> bool:
        return (self.visited, self.current, self.distance) == (other.visited, other.current, other.distance)
    
    def next_hikes(self) -> list["JunctionHike"]:
        hikes = list[JunctionHike]()
        for n, d in self.graph.get(self.current, {}).items():
            if n in self.visited:
                continue
            hikes.append(JunctionHike(
                self.graph,
                self.visited | {self.current},
                n,
                self.distance + d
            ))
        return hikes


class Problem23(Problem):
    def __init__(self, park: Park):
        self.park = park
    
    @classmethod
    def from_str(cls, input: str) -> "Problem23":
        return Problem23(Park.from_str(input))


class Solution23(Solution):
    def solve(self, park: Park) -> int:
        # adjacency matrix between different junctions, dead ends, start and end points
        junction_graph = dict[Vector, dict[Vector, int]]()
        for v in park.junctions:
            junction_graph[v] = {}
            for n, s in park.neighboring_junctions_of(v).items():
                junction_graph[v][n] = len(s)
        starting_hike = JunctionHike(junction_graph, set(), park.start, 0)
        longest: int = 0
        stack: list[JunctionHike] = [starting_hike]
        while len(stack) >= 1:
            hike = stack.pop()
            if hike.current == park.end:
                longest = max(longest, hike.distance)
            for n in hike.next_hikes():
                stack.append(n)
        return longest
    
    def p1(self, problem: Problem23) -> int:
        return self.solve(problem.park)
    
    def p2(self, problem: Problem23) -> int:
        return self.solve(problem.park.to_p2())