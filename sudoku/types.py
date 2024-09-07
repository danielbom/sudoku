from dataclasses import dataclass
from typing import List, NamedTuple, Tuple

Puzzle = List[List[int]]
Coord = Tuple[int, int]
Cage = List[Coord]


class Blocks(NamedTuple):
    curr: Tuple[int]
    up: Tuple[int]
    down: Tuple[int]
    left: Tuple[int]
    right: Tuple[int]


@dataclass
class Game:
    puzzle: Puzzle
    cages: List[Cage]
    rules: List[str]
