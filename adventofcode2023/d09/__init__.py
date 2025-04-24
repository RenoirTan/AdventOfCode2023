from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


def get_diffs(history: list[int]) -> list[int]:
    return [b - a for a, b in zip(history, history[1:])]


def all_zeroes(it: list[int]) -> bool:
    return all((i == 0) for i in it)


def get_nested_diffs(history: list[int]) -> list[list[int]]:
    nested = [history.copy()]
    while not all_zeroes(diff := get_diffs(nested[-1])):
        nested.append(diff)
    return nested


class Problem09(Problem):
    def __init__(self, histories: list[list[int]]):
        self.histories = histories
    
    @classmethod
    def from_str(cls, input: str) -> "Problem09":
        lines = input.splitlines()
        histories = [[int(val) for val in line.split(" ")] for line in lines]
        return Problem09(histories)


class Solution09(Solution):
    def p1(self, problem: Problem09) -> int:
        total = 0
        for history in problem.histories:
            nested = get_nested_diffs(history)
            extrapolated = nested[-1][-1]
            for layer in nested[-2::-1]: # second deepest layer to original history
                extrapolated += layer[-1]
            total += extrapolated
        return total
    
    def p2(self, problem: Problem09) -> int:
        total = 0
        for history in problem.histories:
            nested = get_nested_diffs(history)
            extrapolated = nested[-1][-1]
            for layer in nested[-2::-1]: # second deepest layer to original history
                extrapolated = layer[0] - extrapolated
            total += extrapolated
        return total