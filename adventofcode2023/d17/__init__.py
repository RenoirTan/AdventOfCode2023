from dataclasses import dataclass
from enum import Enum
import heapq
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


@dataclass
class Node(object):
    """
    Instead of having the individual cells in the map be the nodes,
    we instead also store include the number of times the same direction has
    been moved in, so now the adjacency matrix includes the coordinates,
    direction and number of moves in the same direction.
    """
    p: Vector
    d: Direction
    s: int
    k: str
    
    def move(self, direction: Direction) -> "Node":
        return Node(
            self.p + direction,
            direction,
            (self.s + 1) if self.d == direction else 1,
            self.k + direction.s
        )
    
    def __eq__(self, other: "Node") -> bool:
        return (self.p, self.d, self.s) == (other.p, other.d, other.s)
    
    def __hash__(self):
        return hash((self.p, self.d, self.s))
    
    def __lt__(self, other: "Node") -> bool:
        return True


class Dijkstra(object):
    def __init__(
        self,
        map: list[list[int]],
        validate_neighbor: t.Callable[[Node, Direction], bool] = lambda n, d: n.s < 3 or n.d != d,
        validate_goal: t.Callable[[Node], bool] = lambda _: True
    ):
        self.map = map
        self.height = len(map)
        self.width = len(map[0])
        start_node = Node(Vector(0, 0), Direction.RIGHT, 0, "")
        self.visited: set[Node] = {start_node}
        self.pq: list[tuple[int, Node]] = [(0, start_node)]
        self.best_heat_loss: int | float = float("inf")
        self.goal = Vector(self.width - 1, self.height - 1)
        self.validate_neighbor = validate_neighbor
        self.validate_goal = validate_goal
    
    def solve(self) -> int | float:
        while self.process_unvisited():
            pass
        return self.best_heat_loss
    
    def process_unvisited(self) -> bool:
        if len(self.pq) <= 0:
            return False
        d, node = heapq.heappop(self.pq)
        if node.p == self.goal and self.validate_goal.__call__(node):
            # By priority queue, the smallest distance will always come out first
            self.best_heat_loss = min(d, self.best_heat_loss)
            return False
        for neighbor in self.valid_neighbors_of(node):
            if neighbor in self.visited:
                continue
            new_distance = d + self.map[neighbor.p.y][neighbor.p.x]
            heapq.heappush(self.pq, (new_distance, neighbor))
            self.visited.add(neighbor)
        return True
    
    def valid_coord(self, v: Vector) -> bool:
        x, y = v.x, v.y
        return x >= 0 and x < self.width and y >= 0 and y < self.height
    
    def valid_neighbors_of(self, n: Node) -> list[Node]:
        neighbors: list[Node] = []
        for direction in Direction:
            if not self.validate_neighbor.__call__(n, direction):
                continue
            if direction + n.d == Vector(0, 0): # cannot reverse
                continue
            new_node = n.move(direction)
            if self.valid_coord(new_node.p):
                neighbors.append(new_node)
        return neighbors


class Problem17(Problem):
    def __init__(self, map: list[list[int]]):
        self.map = map
    
    @classmethod
    def from_str(cls, input: str) -> "Problem17":
        map = [[int(c) for c in row] for row in input.splitlines()]
        return Problem17(map)


class Solution17(Solution):
    def p1(self, problem: Problem17) -> int:
        dijkstra = Dijkstra(problem.map)
        return dijkstra.solve()
    
    def p2(self, problem: Problem17) -> int:
        dijkstra = Dijkstra(
            problem.map,
            lambda n, d: n.s <= 10 and not (n.s < 4 and n.d != d),
            lambda n: n.s >= 4
        )
        return dijkstra.solve()