from functools import reduce

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


def big_hash_once(accumulator: int, character: int) -> int:
    return ((accumulator + character) * 17) % 256


def big_hash(input: str) -> int:
    return reduce(big_hash_once, (ord(c) for c in input), 0)


def decode_step(step: str) -> tuple[str, int]:
    """
    Convert a step into a pair containing a label and an integer representing
    the focal length if at least 1 or to remove the lens if equal to 0
    """
    if step[-1] == "-":
        return step[:-1], 0
    else:
        label, focal = step.split("=")
        return label, int(focal)


class Problem15(Problem):
    def __init__(self, steps: list[str]):
        self.steps = steps
    
    @classmethod
    def from_str(cls, input: str) -> "Problem15":
        return Problem15(input.split(","))


class Solution15(Solution):
    def p1(self, problem: Problem15) -> int:
        return sum(map(big_hash, problem.steps))
    
    def p2(self, problem: Problem15) -> int:
        decoded_steps = (decode_step(step) for step in problem.steps)
        boxes: list[list[tuple[str, int]]] = [[] for _ in range(256)]
        for label, focal in decoded_steps:
            box = boxes[big_hash(label)]
            if focal == 0: # remove
                for i in range(len(box)):
                    if box[i][0] == label:
                        box.pop(i)
                        break
            else:
                for i in range(len(box)):
                    if box[i][0] == label:
                        box[i] = label, focal
                        break
                else:
                    box.append((label, focal))
        power = 0
        for b, box in enumerate(boxes):
            for s, (_label, length) in enumerate(box):
                power += (b + 1) * (s + 1) * length
        return power