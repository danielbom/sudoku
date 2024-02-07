
import functools
from typing import List, Tuple

from .types import Blocks, Puzzle


blocks_indexes = [
    # (curr_ix, up_ix, down_ix, left_ix, right_ix)
    (0, 6, 3, 2, 1),
    (1, 7, 4, 0, 2),
    (2, 8, 5, 1, 0),
    (3, 0, 6, 5, 4),
    (4, 1, 7, 3, 5),
    (5, 2, 8, 4, 3),
    (6, 3, 0, 8, 7),
    (7, 4, 1, 6, 8),
    (8, 5, 2, 7, 6),
]


def remove_zeros(xs: List[int]) -> List[int]:
    return [x for x in xs if x != 0]


def compute_block_index(row_ix: int, col_ix: int):
    return row_ix // 3 * 3 + col_ix // 3


def check_values_is_valid(values: List[int]):
    values = remove_zeros(values)
    return len(set(values)) == len(values)


def check_values_is_complete(values: List[int]):
    return all(x != 0 for x in values)


def check_puzzle_is_valid(puzzle: Puzzle):
    rows = (row for row in puzzle)
    cols = ([puzzle[i][j] for i in range(9)] for j in range(9))
    blocks = (collect_puzzle_block(puzzle, block_ix) for block_ix in range(9))
    return all(check_values_is_valid(values)
               for many_values in [rows, cols, blocks]
               for values in many_values)


def check_puzzle_is_solution(puzzle: Puzzle, solution: Puzzle):
    return (
        check_puzzle_is_complete(solution) and
        check_puzzle_is_valid(solution) and
        all(puzzle[i][j] == 0 or puzzle[i][j] == solution[i][j]
            for i in range(9) for j in range(9))
    )


@functools.lru_cache(maxsize=None)
def check_blocks_is_valid(blocks: Blocks):
    rows, cols = collect_rows_and_cols(blocks)
    return all(map(check_values_is_valid, rows)) and all(map(check_values_is_valid, cols)) and check_values_is_valid(blocks.curr)


def collect_rows_and_cols(blocks: Blocks):
    rows = [
        blocks.left[0:3] + blocks.curr[0:3] + blocks.right[0:3],
        blocks.left[3:6] + blocks.curr[3:6] + blocks.right[3:6],
        blocks.left[6:9] + blocks.curr[6:9] + blocks.right[6:9],
    ]
    cols = [
        [blocks.up[0], blocks.up[3], blocks.up[6], blocks.curr[0], blocks.curr[3],
            blocks.curr[6], blocks.down[0], blocks.down[3], blocks.down[6]],
        [blocks.up[1], blocks.up[4], blocks.up[7], blocks.curr[1], blocks.curr[4],
            blocks.curr[7], blocks.down[1], blocks.down[4], blocks.down[7]],
        [blocks.up[2], blocks.up[5], blocks.up[8], blocks.curr[2], blocks.curr[5],
            blocks.curr[8], blocks.down[2], blocks.down[5], blocks.down[8]],
    ]
    return rows, cols


def collect_block_indexes(block_ix: int) -> List[Tuple[int, int]]:
    block_row = block_ix // 3
    block_col = block_ix % 3
    return [(i + block_row * 3, j + block_col * 3) for i in range(3) for j in range(3)]


def collect_puzzle_block(puzzle: Puzzle, block_ix: int) -> List[int]:
    return [puzzle[i][j] for i, j in collect_block_indexes(block_ix)]


def collect_puzzle_blocks(puzzle: Puzzle, block_ix: int) -> Blocks:
    (curr_ix, up_ix, down_ix, left_ix, right_ix) = blocks_indexes[block_ix]
    return Blocks(
        tuple(collect_puzzle_block(puzzle, curr_ix)),
        tuple(collect_puzzle_block(puzzle, up_ix)),
        tuple(collect_puzzle_block(puzzle, down_ix)),
        tuple(collect_puzzle_block(puzzle, left_ix)),
        tuple(collect_puzzle_block(puzzle, right_ix)),
    )


def check_puzzle_is_complete(puzzle: Puzzle):
    return all(map(check_values_is_complete, puzzle))


def why_is_invalid(puzzle: Puzzle):
    print("Rows: ")
    for i in range(9):
        row = puzzle[i]
        if not check_values_is_valid(row):
            print(i, row, "row INVALID")
        elif check_values_is_complete(row):
            print(i, row, "row VALID and COMPLETE")
        else:
            print(i, row, "row VALID and NOT COMPLETE")

    print("Cols: ")
    for j in range(9):
        col = [puzzle[i][j] for i in range(9)]
        if not check_values_is_valid(col):
            print(j, col, "col INVALID")
        elif check_values_is_complete(col):
            print(j, col, "col VALID and COMPLETE")
        else:
            print(j, col, "col VALID and NOT COMPLETE")

    print("Blocks: ")
    for block_ix in range(9):
        block = collect_puzzle_block(puzzle, block_ix)
        if not check_values_is_valid(block):
            print(block_ix, block, "block INVALID")
        elif check_values_is_complete(block):
            print(block_ix, block, "block VALID and COMPLETE")
        else:
            print(block_ix, block, "block VALID and NOT COMPLETE")


def puzzle_from_csv(file_path: str) -> Puzzle:
    with open(file_path) as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]
        rows = [line.split(",") for line in lines]
        puzzle = [[int(cell.strip()) for cell in row] for row in rows]
        if len(puzzle) != 9:
            raise ValueError("Puzzle must have 9 rows")
        for row in puzzle:
            if len(row) != 9:
                raise ValueError("Each row must have 9 cells")
        return puzzle


def puzzle_display(puzzle: Puzzle):
    for row in puzzle:
        print(*row, sep=", ")


def puzzle_copy(puzzle: Puzzle) -> Puzzle:
    return [row.copy() for row in puzzle]
