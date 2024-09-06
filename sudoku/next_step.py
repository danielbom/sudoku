from collections import defaultdict
from typing import List

from .helpers import collect_puzzle_block, compute_block_index, remove_zeros
from .types import Coord, Puzzle


class NextStep:
    def __init__(self, next_step_func, start=(0, 0)):
        self.next_step_func = next_step_func
        self.start = start

    def next(self, row_ix: int, col_ix: int):
        return self.next_step_func(row_ix, col_ix)


def compute_next_step(row_ix: int, col_ix: int):
    next_row_ix = row_ix
    next_col_ix = col_ix + 1
    if next_col_ix == 9:
        next_row_ix += 1
        next_col_ix = 0
    return next_row_ix, next_col_ix


def make_compute_next_step(_puzzle: Puzzle):
    return NextStep(compute_next_step)


def compute_next_step_block_column(row_ix: int, col_ix: int):
    next_row_ix = row_ix
    next_col_ix = col_ix + 1
    if next_col_ix % 3 == 0:
        next_col_ix -= 3
        next_row_ix += 1
    if next_row_ix == 9 and next_col_ix in [0, 3, 6]:
        next_row_ix = 0
        next_col_ix += 3
    return next_row_ix, next_col_ix


def make_compute_next_step_block_column(_puzzle: Puzzle):
    return NextStep(compute_next_step_block_column)


def compute_next_step_block_row(row_ix: int, col_ix: int):
    next_row_ix = row_ix + 1
    next_col_ix = col_ix
    if next_row_ix % 3 == 0:
        next_row_ix -= 3
        next_col_ix += 1
    if next_col_ix == 9 and next_row_ix in [0, 3, 6]:
        next_col_ix = 0
        next_row_ix += 3
    return next_row_ix, next_col_ix


def make_compute_next_step_block_row(_puzzle: Puzzle):
    return NextStep(compute_next_step_block_row)


def compute_best_path_next_step2(puzzle: Puzzle) -> List[Coord]:
    blocks = [set(remove_zeros(collect_puzzle_block(puzzle, i)))
              for i in range(9)]
    rows = [set(remove_zeros(puzzle[i]))
            for i in range(9)]
    cols = [set(remove_zeros([puzzle[i][j]for i in range(9)]))
            for j in range(9)]
    options = [(set(range(1, 10)) - blocks[compute_block_index(i, j)] - rows[i] - cols[j], (i, j))
               for i in range(9)
               for j in range(9)]
    options.sort(key=lambda pair: (compute_block_index(
        pair[1][0], pair[1][1]), len(pair[0])))
    return [pair[1] for pair in options]


def compute_best_path_next_step1(puzzle: Puzzle) -> List[Coord]:
    blocks_sizes = sorted([(len(remove_zeros(collect_puzzle_block(puzzle, block_ix))), block_ix)
                           for block_ix in range(9)])
    blocks = [pair[1] for pair in blocks_sizes]

    rows_sizes = sorted([(len(remove_zeros(puzzle[row_ix])), row_ix)
                         for row_ix in range(9)])
    rows = [pair[1] for pair in sorted(rows_sizes)]

    cols_sizes = sorted([(len(remove_zeros([puzzle[i][col_ix] for i in range(9)])), col_ix)
                         for col_ix in range(9)])
    cols = [pair[1] for pair in sorted(cols_sizes)]

    path = []
    for row_ix in range(9):
        for col_ix in range(9):
            if puzzle[row_ix][col_ix] == 0:
                path.append((row_ix, col_ix))

    sorter = []
    if sum(1 for pair in blocks_sizes if pair[0] < 3) < 5:
        blocks_sum = sum(pair[0] for pair in blocks_sizes[-3:])
        sorter.append((blocks_sum, lambda p: blocks.index(
            compute_block_index(p[0], p[1]))))
    if sum(1 for pair in rows_sizes if pair[0] < 3) < 5:
        rows_sum = sum(pair[0] for pair in rows_sizes[-3:])
        sorter.append((rows_sum, lambda p: rows.index(p[0])))
    if sum(1 for pair in cols_sizes if pair[0] < 3) < 5:
        cols_sum = sum(pair[0] for pair in cols_sizes[-3:])
        sorter.append((cols_sum, lambda p: cols.index(p[1])))

    if sorter:
        sorter = sorted(sorter, key=lambda pair: pair[0])
        return sorted(path,
                      key=lambda p: tuple([f[1](p) for f in sorter]),
                      reverse=True)

    return path


def _make_compute_next_step_heuristic(compute_best_path_next_step):
    def make_compute_next_step_heuristic(puzzle: Puzzle):
        best_path_next_step = compute_best_path_next_step(puzzle)

        path_dict = defaultdict(lambda: (9, 9))
        for i in range(len(best_path_next_step) - 1):
            path_dict[best_path_next_step[i]] = best_path_next_step[i + 1]

        def compute_next_step_heuristic(row_ix: int, col_ix: int):
            return path_dict[(row_ix, col_ix)]

        return NextStep(compute_next_step_heuristic, best_path_next_step[0])

    return make_compute_next_step_heuristic


make_compute_next_step_heuristic1 = _make_compute_next_step_heuristic(
    compute_best_path_next_step1)
make_compute_next_step_heuristic2 = _make_compute_next_step_heuristic(
    compute_best_path_next_step2)
