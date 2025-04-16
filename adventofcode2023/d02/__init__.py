from dataclasses import dataclass
import re

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


RED_RE = re.compile(r"(?P<n>\d+) red")
GREEN_RE = re.compile(r"(?P<n>\d+) green")
BLUE_RE = re.compile(r"(?P<n>\d+) blue")
GAME_RE = re.compile(r"Game (?P<id>\d+)")


@dataclass
class Pick(object):
    red: int = 0
    green: int = 0
    blue: int = 0
    
    @classmethod
    def from_str(cls, input: str) -> "Pick":
        red = RED_RE.search(input)
        red = int(red.group("n")) if red else 0
        green = GREEN_RE.search(input)
        green = int(green.group("n")) if green else 0
        blue = BLUE_RE.search(input)
        blue = int(blue.group("n")) if blue else 0
        return Pick(red=red, green=green, blue=blue)
    
    def is_ok(self, context: tuple[int, int, int]) -> bool:
        return self.red <= context[0] and self.green <= context[1] and self.blue <= context[2]


@dataclass
class Game(object):
    id: int
    picks: list[Pick]
    
    @classmethod
    def from_str(cls, input: str) -> "Game":
        id_picks = input.split(":")
        id = int(GAME_RE.match(id_picks[0]).group("id"))
        picks = [Pick.from_str(p) for p in id_picks[1].split(";")]
        return Game(id=id, picks=picks)
    
    def min_context(self) -> tuple[int, int, int]:
        red = max(pick.red for pick in self.picks)
        green = max(pick.green for pick in self.picks)
        blue = max(pick.blue for pick in self.picks)
        return red, green, blue
    
    def min_context_power(self) -> int:
        red, green, blue = self.min_context()
        return red * green * blue


class Problem02(Problem):
    def __init__(self, games: list[Game], context: tuple[int, int, int] = (12, 13, 14)):
        self.games: list[Game] = games
        self.context: tuple[int, int, int] = context
    
    @classmethod
    def from_str(cls, input: str) -> "Problem02":
        games = [Game.from_str(l) for l in input.splitlines()]
        return Problem02(games=games)


class Solution02(Solution):
    def p1(self, problem: Problem02) -> int:
        return sum(p1_indiv(game, problem.context) for game in problem.games)
    
    def p2(self, problem: Problem02) -> int:
        return sum(game.min_context_power() for game in problem.games)


def p1_indiv(game: Game, context: tuple[int, int, int]) -> int:
    return game.id if all(pick.is_ok(context) for pick in game.picks) else 0