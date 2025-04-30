from dataclasses import dataclass
from functools import cache

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@cache
def record_combos(row: str, sizes: tuple[int, ...]) -> int:
    if len(row) == 0:
        return int(len(sizes) == 0)
    row_size = len(row)
    match row[0]:
        case ".":
            i = 0
            while i < row_size:
                if row[i] == ".":
                    i += 1
                else:
                    break
            return record_combos(row[i:], sizes)
        case "?":
            # sum of number of combinations starting with '.' and
            # those starting with '#'
            return record_combos(row[1:], sizes) + record_combos("#" + row[1:], sizes)
        case "#":
            if len(sizes) == 0 or row_size < sizes[0]:
                return 0
            # check if prefix of the row can contain a stretch of damaged
            # springs whose length equals sizes[0]
            if all(c == "#" or c == "?" for c in row[:sizes[0]]):
                # implies prefix has length greater than first stretch
                if row_size > sizes[0] and row[sizes[0]] == "#":
                    return 0
                else:
                    return record_combos(row[sizes[0]+1:], sizes[1:])
            else:
                return 0


@dataclass
class Record(object):
    row: str
    sizes: list[int]
    
    @classmethod
    def from_str(cls, input: str) -> "Record":
        row, sizes = input.split(" ")
        sizes = [int(s) for s in sizes.split(",")]
        return Record(row, sizes)
    
    def combos(self) -> int:
        return record_combos(self.row, tuple(self.sizes))


class Problem12(Problem):
    def __init__(self, records: list[Record]):
        self.records = records
    
    @classmethod
    def from_str(cls, input: str) -> "Problem12":
        return Problem12([Record.from_str(line) for line in input.splitlines()])


class Solution12(Solution):
    def p1(self, problem: Problem12) -> int:
        return sum(record.combos() for record in problem.records)
    
    def p2(self, problem: Problem12, unfolding: int = 5) -> int:
        return sum(
            Record("?".join([record.row]*unfolding), record.sizes*unfolding).combos()
            for record in problem.records
        )