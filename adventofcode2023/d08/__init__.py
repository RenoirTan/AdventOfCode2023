from dataclasses import dataclass
import math
import typing as t

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass
class Node(object):
    value: str
    left: str
    right: str
    
    @classmethod
    def from_str(cls, input: str) -> "Node":
        value = input[0:3]
        left = input[7:10]
        right = input[12:15]
        return Node(value, left, right)


class Problem08(Problem):
    def __init__(self, instructions: str, nodes: dict[str, Node]):
        self.instructions = instructions
        self.nodes = nodes
    
    @classmethod
    def from_str(cls, input: str) -> "Problem08":
        lines = input.splitlines()
        instructions = lines[0]
        nodes = {node.value: node for node in (Node.from_str(line) for line in lines[2:])}
        return Problem08(instructions, nodes)


class Solution08(Solution):
    def p1(
        self,
        problem: Problem08,
        starting_node: str = "AAA",
        matcher: t.Callable[[str], bool] | None = None
    ) -> int:
        matcher = (lambda s: s == "ZZZ") if matcher is None else matcher
        steps = 1
        current_node = problem.nodes[starting_node]
        while True:
            for instruction in problem.instructions:
                match instruction:
                    case "L":
                        current_node = problem.nodes[current_node.left]
                    case "R":
                        current_node = problem.nodes[current_node.right]
                if matcher(current_node.value):
                    return steps
                else:
                    steps += 1
    
    def p2(self, problem: Problem08) -> int:
        starting_nodes = [name for name in problem.nodes.keys() if name.endswith("A")]
        steps_required = [
            self.p1(problem, start, lambda s: s.endswith("Z"))
            for start in starting_nodes
        ]
        # assumes no substring of instructions repeats the entire thing
        return math.lcm(*steps_required)