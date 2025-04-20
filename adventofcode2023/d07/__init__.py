from collections import Counter
from dataclasses import dataclass
from enum import Enum
from functools import cache, reduce

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


def stretch_length(it: list[int]) -> int:
    n = len(it)
    if n <= 0:
        return 0
    for i in range(1, n):
        if it[i] != it[0]:
            return i
    return n


def stretches_of(it: list[int]) -> Counter:
    i = 0
    n = len(it)
    c = Counter()
    while i < n:
        l = stretch_length(it[i:])
        i += l
        c[l] += 1
    return c


@cache
def count_js(rep: str) -> int:
    return len("".join(filter(lambda c: c == "J", rep)))


class HandType(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    FULL_HOUSE = 5
    FOUR_OF_A_KIND = 6
    FIVE_OF_A_KIND = 7


LABELS = {str(i): i for i in range(2, 10)} | {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
LABELS_WILDCARD = LABELS.copy()
LABELS_WILDCARD["J"] = 1


@dataclass
class Hand(object):
    representation: str
    bid: int
    wildcard_joker: bool = False

    @property
    # @cache
    def labels(self) -> list[int]:
        if self.wildcard_joker:
            return [LABELS_WILDCARD[l] for l in self.representation]
        else:
            return [LABELS[l] for l in self.representation]

    @property
    # @cache
    def hand_type(self) -> HandType:
        labels = sorted(self.labels)
        stretches = stretches_of(labels)
        
        if self.wildcard_joker:
            js = count_js(self.representation)
            if 1 <= js <= 4:
                stretches[js] -= 1
                longest = max(k for k, v in stretches.items() if v >= 1)
                stretches[longest] -= 1
                stretches[js + longest] += 1
        
        if stretches[5] == 1:
            return HandType.FIVE_OF_A_KIND
        elif stretches[4] == 1:
            return HandType.FOUR_OF_A_KIND
        elif stretches[3] == 1:
            if stretches[2] == 1:
                return HandType.FULL_HOUSE
            else:
                return HandType.THREE_OF_A_KIND
        elif (s2 := stretches[2]) == 2:
            return HandType.TWO_PAIR
        elif s2 == 1:
            return HandType.ONE_PAIR
        else:
            return HandType.HIGH_CARD
    
    @classmethod
    def from_str(cls, line: str) -> "Hand":
        return Hand(line[:5], int(line[6:]))
    
    def __eq__(self, other: "Hand") -> bool:
        return self.representation == other.representation
    
    def __lt__(self, other: "Hand") -> bool:
        if self == other:
            return False
        elif (sv := self.hand_type.value) < (ov := other.hand_type.value):
            return True
        elif sv == ov:
            return self.labels < other.labels
        else:
            return False
    
    def __gt__(self, other: "Hand") -> bool:
        return other < self


class Problem07(Problem):
    def __init__(self, hands: list[Hand]):
        self.hands = hands
    
    @classmethod
    def from_str(cls, input: str) -> "Problem07":
        lines = input.splitlines()
        hands = [Hand.from_str(l) for l in lines]
        return Problem07(hands)
    

class Solution07(Solution):
    def p1(self, problem: Problem07) -> int:
        ranked = sorted(problem.hands)
        winnings = sum((i + 1) * hand.bid for i, hand in enumerate(ranked))
        return winnings
    
    def p2(self, problem: Problem07) -> int:
        for hand in problem.hands:
            hand.wildcard_joker = True
        return self.p1(problem)