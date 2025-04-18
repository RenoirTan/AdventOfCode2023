from collections import Counter
from dataclasses import dataclass

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass
class Card(object):
    winning: set[int]
    given: set[int]
    
    def get_winning_numbers(self) -> set[int]:
        return self.winning & self.given
    
    def get_points(self) -> int:
        return (1 << len(self.get_winning_numbers())) >> 1


class Problem04(Problem):
    def __init__(self, cards: list[Card]):
        self.cards = cards
    
    @classmethod
    def from_str(cls, input: str) -> "Problem04":
        cards = []
        for line in input.splitlines():
            winning, given = line[line.find(":"):].split("|")
            winning = {int(i) for i in winning.split(" ") if i.isdigit()}
            given = {int(i) for i in given.split(" ") if i.isdigit()}
            cards.append(Card(winning, given))
        return Problem04(cards)


class Solution04(Solution):
    def p1(self, problem: Problem04) -> int:
        return sum(card.get_points() for card in problem.cards)
    
    def p2(self, problem: Problem04) -> int:
        n_cards = len(problem.cards)
        counter = Counter(range(n_cards)) # get one of each card
        for i, card in enumerate(problem.cards):
            points = len(card.get_winning_numbers())
            copies = counter[i]
            window = range(i+1, min(i+1+points, n_cards))
            # get extra cards based on the number of copies of the current card you have
            extra = Counter({k: v * copies for k, v in Counter(window).items()})
            counter += extra
        return sum(counter.values())