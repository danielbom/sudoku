from typing import List, NamedTuple, Tuple


Puzzle = List[List[int]]
Coord = Tuple[int, int]


class Blocks(NamedTuple):
    curr: Tuple[int]
    up: Tuple[int]
    down: Tuple[int]
    left: Tuple[int]
    right: Tuple[int]
