from dataclasses import dataclass
from enum import Enum

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


class Rock(Enum):
    EMPTY = "."
    ROUND = "O"
    CUBE = "#"


def tilt_left(row: list[Rock]) -> list[Rock]:
    new_row = []
    round_counter = 0
    prev_cube = -1
    
    def insert_rocks(i: int):
        empty_counter = i - prev_cube - 1 - round_counter
        assert empty_counter >= 0
        new_row.extend([Rock.ROUND] * round_counter + [Rock.EMPTY] * empty_counter + [Rock.CUBE])
    
    for i, rock in enumerate(row):
        match rock:
            case Rock.ROUND: round_counter += 1
            case Rock.CUBE:
                insert_rocks(i)
                prev_cube = i
                round_counter = 0
    else:
        insert_rocks(len(row))
        new_row.pop() # remove last cube
    return new_row


def load_left(row: list[Rock], length: int = None) -> int:
    length = length or len(row)
    return sum((length - x) if row[x] == Rock.ROUND else 0 for x in range(length))


@dataclass
class Platform(object):
    rocks: list[list[Rock]]
    
    def clone_empty_and_cube(self) -> "Platform":
        rocks = [[Rock.EMPTY if c == Rock.EMPTY else Rock.CUBE for c in row] for row in self.rocks]
        return Platform(rocks)
    
    def transpose(self) -> "Platform":
        height = len(self.rocks)
        width = len(self.rocks[0])
        return Platform([[self.rocks[y][x] for y in range(height)] for x in range(width)])
    
    def reverse_horizontally(self) -> "Platform":
        width = len(self.rocks[0])
        return Platform([[row[-x-1] for x in range(width)] for row in self.rocks])
    
    def tilt_west(self) -> "Platform":
        return Platform([tilt_left(row) for row in self.rocks])
    
    def tilt_north(self) -> "Platform":
        return self.transpose().tilt_west().transpose()
    
    def tilt_east(self) -> "Platform":
        return self.reverse_horizontally().tilt_west().reverse_horizontally()
    
    def tilt_south(self) -> "Platform":
        return self.transpose().reverse_horizontally()\
            .tilt_west()\
            .reverse_horizontally().transpose()
    
    def tilt_cycle(self) -> "Platform":
        return self.tilt_north().tilt_west().tilt_south().tilt_east()
    
    def tilt_cycles(self, n: int = 1000000000) -> "Platform":
        visited: dict[Platform, int] = {}
        this = self
        for i in range(n):
            if (j := visited.get(this)) is None:
                visited[this] = i
                this = this.tilt_cycle()
            else:
                # k is the index of the first time the platform that matches
                # the platform at step n occurs
                k = j + ((n - i) % (i - j)) # n - j is remaning steps, i - j is cycle length
                for platform, i in visited.items():
                    if k == i:
                        return platform
        return this
        
    
    def load_north(self) -> int:
        height = len(self.rocks)
        width = len(self.rocks[0])
        return sum(load_left([row[x] for row in self.rocks], height) for x in range(width))
    
    def __hash__(self):
        return hash(str(self))
    
    def __str__(self) -> str:
        return "\n".join("".join(rock.value for rock in row) for row in self.rocks)


class Problem14(Problem):
    def __init__(self, platform: Platform):
        self.platform = platform
    
    @classmethod
    def from_str(cls, input: str) -> "Problem14":
        platform = [[Rock(c) for c in row] for row in input.splitlines()]
        return Problem14(Platform(platform))


class Solution14(Solution):
    def p1(self, problem: Problem14) -> int:
        return problem.platform.tilt_north().load_north()
    
    def p2(self, problem: Problem14) -> int:
        return problem.platform.tilt_cycles().load_north()