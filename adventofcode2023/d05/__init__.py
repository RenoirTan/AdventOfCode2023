from dataclasses import dataclass
import re

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


MAP_HEADER_RE = re.compile(r"^.* map:$")


def subtract_range_from_range(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Subtract range b from range a, leaving a list of remaining ranges
    """
    result: list[tuple[int, int]] = []
    if b[0] > a[0]:
        result.append((a[0], min(b[0], a[1])))
    if b[1] < a[1]:
        result.append((max(b[1], a[0]), a[1]))
    return result


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    result = sorted(ranges)
    i = 0
    while i < len(result) - 1:
        a = result[i]
        b = result[i+1]
        # disjoint
        if a[1] < b[0] or a[0] > b[1]:
            i += 1
        else: # merge both ranges and replace them
            c = min(a[0], b[0]), max(a[1], b[1])
            result[i:i+2] = [c]
    return result


@dataclass
class ConversionResult(object):
    changed: list[tuple[int, int]]
    unchanged: list[tuple[int, int]]
    
    def combine(self) -> list[tuple[int, int]]:
        return merge_ranges(self.changed + self.unchanged)


@dataclass
class MappingRange(object):
    dest_start: int
    src_start: int
    length: int
    
    @property
    def src_end(self) -> int:
        return self.src_start + self.length
    
    @property
    def diff(self) -> int:
        return self.dest_start - self.src_start
    
    def contains_src(self, src: int) -> bool:
        return 0 <= (src - self.src_start) < self.length
    
    def convert_src(self, src: int) -> int:
        if self.contains_src(src):
            return src + self.dest_start - self.src_start
        else:
            return src
    
    def contained_src_range(self, src_range: tuple[int, int]) -> tuple[int, int]:
        start = max(src_range[0], self.src_start)
        end = max(min(src_range[1], self.src_end), start)
        return start, end
    
    def convert_src_range(self, src_range: tuple[int, int]) -> ConversionResult:
        contained_range = self.contained_src_range(src_range)
        if contained_range[0] >= contained_range[1]:
            return ConversionResult(changed=[], unchanged=[src_range])
        unchanged = subtract_range_from_range(src_range, contained_range)
        changed = contained_range[0] + self.diff, contained_range[1] + self.diff
        return ConversionResult(unchanged=unchanged, changed=[changed])
    
    @classmethod
    def from_str(cls, line: str) -> "MappingRange":
        splat = line.split(" ")
        if len(splat) != 3:
            raise ValueError("MappingRange only has 3 values")
        dest_start = int(splat[0])
        src_start = int(splat[1])
        length = int(splat[2])
        return MappingRange(dest_start, src_start, length)


@dataclass
class MappingCollection(object):
    ranges: list[MappingRange]
    
    def find_containing_ranges(self, src: int) -> list[MappingRange]:
        return [r for r in self.ranges if r.contains_src(src)]
    
    def convert_src(self, src: int) -> int:
        containing_ranges = self.find_containing_ranges(src)
        if not containing_ranges:
            return src
        elif len(containing_ranges) == 1:
            return containing_ranges[0].convert_src(src)
        else:
            raise ValueError("multiple ranges contain the same src")
    
    def convert_src_ranges(self, src_ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        conversion_result = ConversionResult(unchanged=src_ranges, changed=[])
        for mapping_range in self.ranges:
            changed = [c for c in conversion_result.changed] # add already changed ranges
            unchanged = []
            for src_range in conversion_result.unchanged:
                cr = mapping_range.convert_src_range(src_range)
                unchanged.extend(cr.unchanged)
                changed.extend(cr.changed)
            conversion_result = ConversionResult(
                changed=merge_ranges(changed),
                unchanged=merge_ranges(unchanged)
            )
        return conversion_result.combine()
    
    @classmethod
    def from_str(self, lines: list[str]) -> "MappingCollection":
        if not MAP_HEADER_RE.match(lines[0]):
            raise ValueError("map header not found")
        ranges: list[MappingRange] = []
        for line in lines[1:]:
            try:
                mapping_range = MappingRange.from_str(line)
            except:
                break
            else:
                ranges.append(mapping_range)
        return MappingCollection(ranges)


@dataclass
class ChainedMappings(object):
    mapping_collections: list[MappingCollection]
    
    def convert_src(self, src: int) -> int:
        dest = src
        for collection in self.mapping_collections:
            dest = collection.convert_src(dest)
        return dest
    
    def convert_src_ranges(self, src_ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        dest_ranges = src_ranges
        for collection in self.mapping_collections:
            dest_ranges = collection.convert_src_ranges(dest_ranges)
        return dest_ranges


class Problem05(Problem):
    def __init__(self, seeds: list[int], chained_mappings: ChainedMappings):
        self.seeds = seeds
        self.chained_mappings = chained_mappings
        self.seed_ranges = [(s, s+l) for s, l in zip(self.seeds[0::2], self.seeds[1::2])]
    
    @classmethod
    def from_str(cls, input: str) -> "Problem05":
        lines = input.splitlines()
        seeds = [int(s) for s in lines[0][7:].split(" ")]
        map_header_indices = [i for i, line in enumerate(lines) if MAP_HEADER_RE.match(line)]
        mapping_collections = [MappingCollection.from_str(lines[i:]) for i in map_header_indices]
        return Problem05(seeds, ChainedMappings(mapping_collections))


class Solution05(Solution):
    def p1(self, problem: Problem05) -> int:
        return min(problem.chained_mappings.convert_src(seed) for seed in problem.seeds)
    
    def p2(self, problem: Problem05) -> int:
        return problem.chained_mappings.convert_src_ranges(problem.seed_ranges)[0][0]