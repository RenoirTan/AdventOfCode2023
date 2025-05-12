from dataclasses import dataclass
from functools import cache
import typing as t

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass(unsafe_hash=True)
class Brick(object):
    xl: int
    xh: int
    yl: int
    yh: int
    zl: int
    zh: int
    
    def __str__(self) -> str:
        return f"({self.xl},{self.yl},{self.zl}~{self.xh},{self.yh},{self.zh})"
    
    @classmethod
    def from_str(cls, input: str) -> "Brick":
        corners = input.strip().split("~")
        xl, yl, zl = tuple(int(i) for i in corners[0].split(","))
        xh, yh, zh = tuple(int(i) for i in corners[1].split(","))
        return Brick(xl, xh, yl, yh, zl, zh)
    
    def fall_onto(self, other: t.Optional["Brick"] = None) -> "Brick":
        if other is not None and self.can_fall_onto(other):
            new_zl = other.zh + 1
            new_zh = new_zl + self.zh - self.zl
            return Brick(self.xl, self.xh, self.yl, self.yh, new_zl, new_zh)
        else:
            return Brick(self.xl, self.xh, self.yl, self.yh, 1, 1 + self.zh - self.zl)
    
    def intersects(self, other: "Brick") -> bool:
        return (
            (self.xl <= other.xh and self.xh >= other.xl)
            and (self.yl <= other.yh and self.yh >= other.yl)
        )
    
    def can_fall_onto(self, other: "Brick") -> bool:
        return self.zl - other.zh >= 1 and self.intersects(other)
    
    def is_supported_by(self, other: "Brick") -> bool:
        return self.zl - other.zh == 1 and self.intersects(other)
    
    def is_stabilized_by(self, others: t.Iterable["Brick"]) -> bool:
        # print(self, "[" + ", ".join(str(b) for b in others) + "]")
        return any(self.is_supported_by(other) for other in others)
    
    def stabilize(self, others: t.Iterable["Brick"]) -> t.Optional["Brick"]:
        if self.zl == 1:
            return None
        relevant = [brick for brick in others if self.can_fall_onto(brick)]
        if len(relevant) <= 0:
            return self.fall_onto()
        highest_brick = max(relevant, key=lambda b: b.zh)
        return None if self.is_supported_by(highest_brick) else self.fall_onto(highest_brick)


@dataclass
class Tetris(object):
    bricks: list[Brick]
    
    def __post_init__(self):
        self.normalize()
    
    def __str__(self) -> str:
        return "[" + ", ".join(str(b) for b in self.bricks) + "]"
    
    def normalize(self):
        self.bricks.sort(key=lambda b: b.zh)

    def is_unstable_without(self, without: int) -> bool:
        destroyed = self.bricks[without]
        base = [brick for brick in self.bricks if brick.zh == destroyed.zh and brick != destroyed]
        dependents = [brick for brick in self.bricks if brick.zl - destroyed.zh == 1]
        if len(dependents) == 0 and any(brick.zl - destroyed.zh > 1 for brick in self.bricks):
            return True
        return not all(brick.is_stabilized_by(base) for brick in dependents)
    
    def fall_once(self) -> int:
        fell = 0
        for i in range(len(self.bricks)):
            new_position = self.bricks[i].stabilize(self.bricks[:i])
            if new_position is None:
                continue
            self.bricks[i] = new_position
            self.normalize()
            fell += 1
        return fell
    
    def stabilize(self) -> int:
        total = 0
        while (x := self.fall_once()) >= 1:
            total += x
        return total
    
    def without(self, index: int) -> "Tetris":
        assert 0 <= index < len(self.bricks)
        return Tetris(self.bricks[:index] + self.bricks[index + 1:])
    
    def raw_bricks(self) -> tuple[Brick, ...]:
        return tuple(self.bricks)
    
    def supporters_of(self, index: int) -> set[int]:
        brick = self.bricks[index]
        return {i for i, s in enumerate(self.bricks) if brick.is_supported_by(s)}


class Problem22(Problem):
    def __init__(self, tetris: Tetris):
        self.tetris = tetris
    
    @classmethod
    def from_str(cls, input: str) -> "Problem22":
        bricks = [Brick.from_str(line) for line in input.splitlines()]
        return Problem22(Tetris(bricks))


class Solution22(Solution):
    def __init__(self):
        super().__init__()
        self.tetris: Tetris | None = None
    
    def tetrify(self, problem: Problem22) -> Tetris:
        if self.tetris is None:
            self.tetris = problem.tetris
            self.tetris.stabilize()
        return self.tetris
    
    def p1(self, problem: Problem22) -> int:
        tetris = self.tetrify(problem)
        return sum(not tetris.is_unstable_without(without=i) for i in range(len(tetris.bricks)))
    
    def p2(self, problem: Problem22) -> int:
        tetris = self.tetrify(problem)
        supporters = {i: tetris.supporters_of(i) for i in range(len(tetris.bricks))}
        supporters = {k: v for k, v in supporters.items() if len(v) != 0}
        total = 0
        for i in range(len(tetris.bricks)):
            removed = {i}
            while True:
                would_fall = {k for k, sups in supporters.items() if sups <= removed}
                if len(would_fall) == len(removed) - 1:
                    total += len(would_fall)
                    break
                removed |= would_fall
        return total