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
    
    def __neg__(self) -> "Vector":
        return Vector(-self.x, -self.y)
    
    def __mul__(self, other: int) -> "Vector":
        return Vector(self.x * other, self.y * other)
    
    def __rmul__(self, other: int) -> "Vector":
        return self * other
    
    def get_cell_inside(self, direction: "Direction", rotation: int) -> "Vector":
        return self + direction.rotate(rotation)


@dataclass(unsafe_hash=True)
class DirectionMixin(Vector):
    s: str


class Direction(DirectionMixin, Enum):
    UP = 0, -1, "U"
    DOWN = 0, 1, "D"
    LEFT = -1, 0, "L"
    RIGHT = 1, 0, "R"
    
    @classmethod
    def from_str(cls, input: str) -> "Direction":
        match input:
            case "U": return Direction.UP
            case "D": return Direction.DOWN
            case "L": return Direction.LEFT
            case "R": return Direction.RIGHT
    
    def ortho_angle_with(self, other: "Direction") -> int:
        # positive is clockwise
        # negative is anticlockwise
        # 0 is co-linear
        return self.x * other.y - self.y * other.x
    
    def rotate(self, rotation: int) -> "Direction":
        r = 0 if rotation == 0 else (1 if rotation > 0 else -1)
        x = self.y * -r
        y = self.x * r
        match x, y:
            case 0, -1: return Direction.UP
            case 0, 1: return Direction.DOWN
            case -1, 0: return Direction.LEFT
            case 1, 0: return Direction.RIGHT
    
    @classmethod
    def overall_rotation(cls, directions: list["Direction"]) -> int:
        ab = zip(directions, directions[1:] + [directions[0]])
        r = sum(a.ortho_angle_with(b) for a, b in ab)
        return r


@dataclass
class Instruction(object):
    direction: Direction
    distance: int
    color: str


class Problem18(Problem):
    def __init__(self, instructions: list[Instruction]):
        self.instructions = instructions
    
    @classmethod
    def from_str(cls, input: str) -> "Problem18":
        instructions = []
        for line in input.splitlines():
            line = line.split(" ")
            instructions.append(Instruction(
                Direction.from_str(line[0]),
                int(line[1]),
                line[2][1:-1]
            ))
        return Problem18(instructions)


class Solution18(Solution):
    # https://en.wikipedia.org/wiki/Shoelace_formula
    # https://en.wikipedia.org/wiki/Pick%27s_theorem
    # A = i + b/2 - 1
    # i + b = A + b/2 + 1 where A is the area from shoelace formula
    def solve(self, instructions: list[Instruction]) -> int:
        double_area = 0
        prev_v = Vector(0, 0)
        v = Vector(0, 0)
        for instruction in instructions:
            v = prev_v + instruction.direction * instruction.distance
            double_area += prev_v.x * v.y - v.x * prev_v.y
            prev_v = v
        a = double_area >> 1
        b = sum(i.distance for i in instructions)
        return a + (b >> 1) + 1
    
    def p1(self, problem: Problem18) -> int:
        return self.solve(problem.instructions)
    
    def p2(self, problem: Problem18) -> int:
        instructions: list[Instruction] = []
        for instruction in problem.instructions:
            color = instruction.color
            match color[-1]:
                case "0": direction = Direction.RIGHT
                case "1": direction = Direction.DOWN
                case "2": direction = Direction.LEFT
                case "3": direction = Direction.UP
            distance = int(color[1:6], base=16)
            instructions.append(Instruction(direction, distance, ""))
        return self.solve(instructions)