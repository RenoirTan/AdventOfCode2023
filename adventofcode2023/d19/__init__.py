from dataclasses import dataclass
import typing as t

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass
class Part(object):
    x: int
    m: int
    a: int
    s: int
    
    def sum(self) -> int:
        return self.x + self.m + self.a + self.s


@dataclass
class FieldRange(object):
    lower: int
    upper: int
    
    def __str__(self) -> str:
        return f"{self.lower}-{self.upper}"
    
    def __len__(self) -> int:
        return max(self.upper - self.lower + 1, 0)
    
    def nullify(self) -> t.Optional["FieldRange"]:
        return None if len(self) <= 0 else self
    
    def bifurcate(
        self,
        lt: bool,
        limit: int
    ) -> tuple[t.Optional["FieldRange"], t.Optional["FieldRange"]]:
        """
        Left side of tuple is done, right side is not done
        """
        if len(self) <= 0:
            return None, None
        if lt:
            return (
                FieldRange(self.lower, min(limit - 1, self.upper)).nullify(),
                FieldRange(max(limit, self.lower), self.upper).nullify()
            )
        else:
            return (
                FieldRange(max(limit + 1, self.lower), self.upper).nullify(),
                FieldRange(self.lower, min(limit, self.upper)).nullify()
            )


@dataclass
class PartRange(object):
    x: FieldRange
    m: FieldRange
    a: FieldRange
    s: FieldRange
    
    def __str__(self) -> str:
        return "{" + ", ".join(f"{f}={str(r)}" for f, r in iter(self)) + "}"
    
    def __iter__(self) -> t.Generator[tuple[str, FieldRange]]:
        yield "x", self.x
        yield "m", self.m
        yield "a", self.a
        yield "s", self.s
    
    def combos(self) -> int:
        return len(self.x) * len(self.m) * len(self.a) * len(self.s)


@dataclass
class Condition(object):
    field: str
    lt: bool
    limit: int
    destination: str
    
    def __str__(self) -> str:
        return self.field + ("<" if self.lt else ">") + str(self.limit) + ":" + self.destination
    
    def check(self, part: Part) -> bool:
        match self.field:
            case "x": f = part.x
            case "m": f = part.m
            case "a": f = part.a
            case "s": f = part.s
        if self.lt:
            return f < self.limit
        else:
            return f > self.limit
    
    def bifurcate(self, part_range: PartRange) -> tuple[PartRange | None, PartRange | None]:
        fields = dict(part_range)
        field_range = fields[self.field]
        done_range, undone_range = field_range.bifurcate(self.lt, self.limit)
        done_fields = dict(fields)
        undone_fields = dict(fields)
        if done_range is not None:
            done_fields[self.field] = done_range
        if undone_range is not None:
            undone_fields[self.field] = undone_range
        return (
            PartRange(**done_fields) if done_range is not None else None,
            PartRange(**undone_fields) if undone_range is not None else None
        )
    
    @classmethod
    def from_str(cls, input: str) -> "Condition":
        field = input[0]
        lt = input[1] == "<"
        colon_idx = input.find(":")
        limit = int(input[2:colon_idx])
        destination = input[colon_idx+1:]
        return Condition(field, lt, limit, destination)


@dataclass
class Workflow(object):
    name: str
    conditions: list[Condition]
    otherwise: str
    
    def __str__(self) -> str:
        return (
            self.name
            + "{"
            + ", ".join(str(c) for c in self.conditions)
            + ", "
            + self.otherwise
            + "}"
        )
    
    def run(self, part: Part) -> str:
        for condition in self.conditions:
            if condition.check(part):
                return condition.destination
        return self.otherwise
    
    def split(self, part_range: PartRange) -> dict[str, list[PartRange]]:
        result: dict[str, list[PartRange]] = {}
        undone = part_range
        for condition in self.conditions:
            done, undone = condition.bifurcate(undone)
            if done is not None:
                rs = result.get(condition.destination, [])
                rs.append(done)
                result[condition.destination] = rs
            if undone is None:
                break
        else:
            rs = result.get(self.otherwise, [])
            rs.append(undone)
            result[self.otherwise] = rs
        # print(str(self))
        # print(str(part_range))
        # print("{" + ", ".join(f"{d} <- [{", ".join(str(s) for s in r)}]" for d, r in result.items()) + "}")
        return result


@dataclass
class Series(object):
    workflows: dict[str, Workflow]
    
    @classmethod
    def from_iter(cls, workflows: t.Iterable[Workflow]) -> "Series":
        ws = {}
        for workflow in workflows:
            ws[workflow.name] = workflow
        return Series(ws)
    
    def run(self, part: Part) -> str:
        name = "in"
        while True:
            workflow = self.workflows[name]
            name = workflow.run(part)
            if name == "R" or name == "A":
                return name


class Problem19(Problem):
    def __init__(self, series: Series, parts: list[Part]):
        self.series = series
        self.parts = parts
    
    @classmethod
    def from_str(cls, input: str) -> "Problem19":
        lines = iter(input.splitlines())
        workflows = []
        for line in lines:
            if line == "":
                break
            name, raw_conditions = line.split("{")
            raw_conditions = raw_conditions[:-1].split(",")
            conditions = [Condition.from_str(raw) for raw in raw_conditions[:-1]]
            otherwise = raw_conditions[-1]
            workflows.append(Workflow(name, conditions, otherwise))
        series = Series.from_iter(workflows)
        parts = []
        for line in lines:
            fields = line[1:-1].split(",")
            x = int(fields[0][2:])
            m = int(fields[1][2:])
            a = int(fields[2][2:])
            s = int(fields[3][2:])
            parts.append(Part(x, m, a, s))
        return Problem19(series, parts)


class Solution19(Solution):
    def p1(self, problem: Problem19) -> int:
        return sum(p.sum() for p in problem.parts if problem.series.run(p) == "A")
    
    def p2(self, problem: Problem19) -> int:
        part_range_lists: dict[str, list[PartRange]] = {"in": [PartRange(
            FieldRange(1, 4000),
            FieldRange(1, 4000),
            FieldRange(1, 4000),
            FieldRange(1, 4000)
        )]}
        while any(w != "A" and w != "R" for w in part_range_lists.keys()):
            new_part_range_lists = {
                "A": part_range_lists.get("A", []),
                "R": part_range_lists.get("R", [])
            }
            for w, part_range_list in part_range_lists.items():
                if w == "A" or w == "R":
                    continue
                workflow = problem.series.workflows[w]
                for part_range in part_range_list:
                    for dest, new_part_ranges in workflow.split(part_range).items():
                        new_part_range_list = new_part_range_lists.get(dest, [])
                        new_part_range_list.extend(new_part_ranges)
                        new_part_range_lists[dest] = new_part_range_list
            # print(new_part_range_lists)
            part_range_lists = new_part_range_lists
        # print("{" + ", ".join(f"{str(pr)} => {pr.combos()}" for pr in part_range_lists["A"]) + "}")
        return sum(pr.combos() for pr in part_range_lists["A"])
