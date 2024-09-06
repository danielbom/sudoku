from typing import List, Tuple

from .helpers import (check_blocks_is_valid, collect_puzzle_block,
                      collect_puzzle_blocks, compute_block_index, puzzle_copy)
from .types import Puzzle


class CollectNextSteps:
    def __init__(self, collector):
        self.collector = collector

    def collect(self, puzzle: Puzzle,
                row_ix: int, col_ix: int,
                next_row_ix: int, next_col_ix: int) -> List[Tuple[Puzzle, int, int]]:
        return self.collector(puzzle, row_ix, col_ix, next_row_ix, next_col_ix)


def collect_valid_options(puzzle: Puzzle,
                          row_ix: int, col_ix: int,
                          next_row_ix: int, next_col_ix: int) -> List[Tuple[Puzzle, int, int]]:
    row = puzzle[row_ix]
    col = [puzzle[i][col_ix] for i in range(9)]
    block = collect_puzzle_block(puzzle, compute_block_index(row_ix, col_ix))
    options = set(range(1, 10)) - set(row) - set(col) - set(block)
    nexts = []
    for option in options:
        puzzle[row_ix][col_ix] = option
        nexts.append((puzzle_copy(puzzle), next_row_ix, next_col_ix))
        puzzle[row_ix][col_ix] = 0
    nexts.reverse()
    return nexts


def make_collect_valid_options():
    return CollectNextSteps(collect_valid_options)


def collect_valid_blocks(puzzle: Puzzle,
                         row_ix: int, col_ix: int,
                         next_row_ix: int, next_col_ix: int) -> List[Tuple[Puzzle, int, int]]:
    nexts = []
    block_ix = compute_block_index(row_ix, col_ix)
    for option in range(1, 10):
        puzzle[row_ix][col_ix] = option
        if check_blocks_is_valid(collect_puzzle_blocks(puzzle, block_ix)):
            nexts.append((puzzle_copy(puzzle), next_row_ix, next_col_ix))
        puzzle[row_ix][col_ix] = 0
    nexts.reverse()
    return nexts


def make_collect_valid_blocks():
    return CollectNextSteps(collect_valid_blocks)
