from dataclasses import dataclass
from pathlib import Path
import subprocess
import typing as t

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass(unsafe_hash=True)
class Vector(object):
    x: int
    y: int
    z: int
    
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)


@dataclass(unsafe_hash=True)
class Hailstone(object):
    p: Vector
    v: Vector
    
    @classmethod
    def from_str(cls, input: str) -> "Hailstone":
        splat = input.split("@")
        px, py, pz = tuple(int(s) for s in splat[0].split(", "))
        vx, vy, vz = tuple(int(s) for s in splat[1].split(", "))
        return Hailstone(Vector(px, py, pz), Vector(vx, vy, vz))
    
    def __str__(self):
        p, v = self.p, self.v
        return f"{p.x}, {p.y}, {p.z} @ {v.x}, {v.y}, {v.z}"
    
    def predict_z(self, time: float, delta_z: int) -> float:
        return self.p.z + time * (self.v.z + delta_z)


class Problem24(Problem):
    def __init__(self, hailstones: list[Hailstone]):
        self.hailstones = hailstones
    
    def yield_four(self) -> t.Generator[tuple[int, int, int, int]]:
        n = len(self.hailstones)
        return (
            (i, j, k, l)
            for i in range(n)
            for j in range(i + 1, n)
            for k in range(j + 1, n)
            for l in range(k + 1, n)
        )
    
    @classmethod
    def from_str(cls, input: str) -> "Problem24":
        return Problem24([Hailstone.from_str(line) for line in input.splitlines()])


def find_intersection_xy_time(
    a: Hailstone,
    b: Hailstone
) -> tuple[float, float, float, float] | None:
    ma = a.v.y / a.v.x
    mb = b.v.y / b.v.x
    if ma == mb: # parallel
        return None
    x_side = ma - mb
    c_side = (b.p.y - mb * b.p.x) - (a.p.y - ma * a.p.x)
    x = c_side / x_side
    y = ma * (x - a.p.x) + a.p.y
    
    def get_time(h: Hailstone) -> float | None:
        diff_x = x - h.p.x
        diff_y = y - h.p.y
        
        def delta(displacement: float, velocity: float) -> float | None:
            if displacement != 0.0 and velocity == 0.0:
                return None
            else:
                return displacement / velocity

        def is_close(x: float, y: float, e: float=1e-06) -> bool:
            return abs(1 - x/y) <= e
        
        x_time = delta(diff_x, h.v.x)
        y_time = delta(diff_y, h.v.y)
        assert x_time is None or y_time is None or is_close(x_time, y_time)
        return y_time if x_time is None else x_time
    
    a_time = get_time(a)
    b_time = get_time(b)
    if a_time is None or b_time is None or a_time < 0.0 or b_time < 0.0:
        return None
    return x, y, a_time, b_time


SAGE_SCRIPT_PATH = (Path(__file__).parent / "y2023d24p2.sage").absolute()


def get_rock_position(a: Hailstone, b: Hailstone, c: Hailstone) -> int:
    args = [
        "/usr/bin/env", "sage", SAGE_SCRIPT_PATH,
        a.p.x, a.p.y, a.p.z, a.v.x, a.v.y, a.v.z,
        b.p.x, b.p.y, b.p.z, b.v.x, b.v.y, b.v.z,
        c.p.x, c.p.y, c.p.z, c.v.x, c.v.y, c.v.z,
    ]
    p = subprocess.run([str(arg) for arg in args], capture_output=True)
    out = p.stdout.decode("utf-8").strip()
    if out.startswith("rpx + rpy + rpz == "):
        return int(out[19:])
    else:
        raise ValueError("No solution")


class Solution24(Solution):
    def p1(self, problem: Problem24) -> int:
        min_coord: int = 200000000000000
        max_coord: int = 400000000000000
        h: int = 0
        hn = len(problem.hailstones)
        for ai in range(hn):
            a = problem.hailstones[ai]
            for bi in range(ai + 1, hn):
                b = problem.hailstones[bi]
                xyab = find_intersection_xy_time(a, b)
                if xyab is None:
                    continue
                x, y, a_time, b_time = xyab
                if not (min_coord <= x <= max_coord and min_coord <= y <= max_coord):
                    continue
                h += 1
        return h
    
    def p2(self, problem: Problem24) -> int:
        return get_rock_position(
            problem.hailstones[0],
            problem.hailstones[1],
            problem.hailstones[2]
        )