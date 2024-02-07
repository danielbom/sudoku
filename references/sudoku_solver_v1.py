from dataclasses import dataclass
from datetime import datetime
import functools
from typing import List, NamedTuple, Optional, Tuple


METRIC_DISPLAY_INTERVAL = 1e10  # 5000


@dataclass
class Metrics:
    puzzle_is_valid = 0
    blocks_is_valid = 0
    puzzle_solve = 0
    puzzle_solve_rec = 0
    start_time = None
    end_time = None

    def start(self):
        self.start_time = datetime.now()

    def end(self):
        self.end_time = datetime.now()

    def display(self):
        print("Metrics: ")
        print("    Blocks Is Valid:  ", self.blocks_is_valid)
        print("    Puzzle Is Valid:  ", self.puzzle_is_valid)
        print("    Puzzle Solve:     ", self.puzzle_solve)
        print("    Puzzle Solve Rec: ", self.puzzle_solve_rec)
        if self.end_time and self.start_time:
            print("    Start:            ", self.start_time)
            print("    End:              ", self.end_time)
            print("    Duration:         ", self.end_time - self.start_time)


Puzzle = List[List[int]]


class Blocks(NamedTuple):
    curr: Tuple[int]
    up: Tuple[int]
    down: Tuple[int]
    left: Tuple[int]
    right: Tuple[int]


metrics = Metrics()
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


def values_is_valid(values: List[int]):
    values = remove_zeros(values)
    return len(set(values)) == len(values)


@functools.lru_cache(maxsize=None)
def blocks_is_valid(blocks: Blocks):
    global metrics
    metrics.blocks_is_valid += 1
    if metrics.blocks_is_valid % METRIC_DISPLAY_INTERVAL == 0:
        metrics.display()
    rows, cols = collect_rows_and_cols(blocks)
    return all(map(values_is_valid, rows)) and all(map(values_is_valid, cols)) and values_is_valid(blocks.curr)


def why_is_invalid(puzzle: Puzzle):
    print("Rows: ")
    for i in range(9):
        row = puzzle[i]
        if not values_is_valid(row):
            print(i, row, "row INVALID")
        elif sum(row) == 45:
            print(i, row, "row VALID and COMPLETE")
        else:
            print(i, row, "row VALID and NOT COMPLETE")

    print("Cols: ")
    for j in range(9):
        col = [puzzle[i][j] for i in range(9)]
        if not values_is_valid(col):
            print(j, col, "col INVALID")
        elif sum(col) == 45:
            print(j, col, "col VALID and COMPLETE")
        else:
            print(j, col, "col VALID and NOT COMPLETE")

    print("Blocks: ")
    for block_ix in range(9):
        block = puzzle_collect_block(puzzle, block_ix)
        if not values_is_valid(block):
            print(block_ix, block, "block INVALID")
        elif sum(block) == 45:
            print(block_ix, block, "block VALID and COMPLETE")
        else:
            print(block_ix, block, "block VALID and NOT COMPLETE")


def collect_block_indexes(block_ix: int) -> List[Tuple[int, int]]:
    block_row = block_ix // 3
    block_col = block_ix % 3
    return [(i + block_row * 3, j + block_col * 3) for i in range(3) for j in range(3)]


def puzzle_collect_block(grid: Puzzle, block_ix: int) -> List[int]:
    return [grid[i][j] for i, j in collect_block_indexes(block_ix)]


def puzzle_collect_blocks(puzzle: Puzzle, block_ix: int) -> Blocks:
    (curr_ix, up_ix, down_ix, left_ix, right_ix) = blocks_indexes[block_ix]
    return Blocks(
        tuple(puzzle_collect_block(puzzle, curr_ix)),
        tuple(puzzle_collect_block(puzzle, up_ix)),
        tuple(puzzle_collect_block(puzzle, down_ix)),
        tuple(puzzle_collect_block(puzzle, left_ix)),
        tuple(puzzle_collect_block(puzzle, right_ix)),
    )


def puzzle_blocks_is_valid(puzzle: Puzzle):
    for block_ix in range(9):
        if not blocks_is_valid(puzzle_collect_blocks(puzzle, block_ix)):
            return False
    return True


def puzzle_is_valid(puzzle: Puzzle):
    global metrics
    metrics.puzzle_is_valid += 1
    return (
        all(values_is_valid(row) for row in puzzle) and
        all(values_is_valid([puzzle[i][j] for i in range(9)]) for j in range(9)) and
        all(values_is_valid(puzzle_collect_block(puzzle, block_ix))
            for block_ix in range(9))
    )


def puzzle_is_complete(puzzle: Puzzle):
    return all(all(cell != 0 for cell in row) for row in puzzle)


def get_next_step(row_ix: int, col_ix: int):
    next_row_ix = row_ix
    next_col_ix = col_ix + 1
    if next_col_ix == 9:
        next_row_ix += 1
        next_col_ix = 0
    return next_row_ix, next_col_ix


def get_next_step_block_column(row_ix: int, col_ix: int):
    next_row_ix = row_ix
    next_col_ix = col_ix + 1
    if next_col_ix % 3 == 0:
        next_col_ix -= 3
        next_row_ix += 1
    if next_row_ix == 9 and next_col_ix in [0, 3, 6]:
        next_row_ix = 0
        next_col_ix += 3
    return next_row_ix, next_col_ix


def get_next_step_block_row(row_ix: int, col_ix: int):
    next_row_ix = row_ix + 1
    next_col_ix = col_ix
    if next_row_ix % 3 == 0:
        next_row_ix -= 3
        next_col_ix += 1
    if next_col_ix == 9 and next_row_ix in [0, 3, 6]:
        next_col_ix = 0
        next_row_ix += 3
    return next_row_ix, next_col_ix


def get_block_index(row_ix: int, col_ix: int):
    return row_ix // 3 * 3 + col_ix // 3


def puzzle_solve_rec(puzzle: Puzzle, row_ix: int = 0, col_ix: int = 0) -> Optional[Puzzle]:
    if row_ix == 9 and col_ix == 0:
        return puzzle

    next_row_ix, next_col_ix = get_next_step(row_ix, col_ix)
    block_ix = get_block_index(row_ix, col_ix)
    if puzzle[row_ix][col_ix] != 0:
        return puzzle_solve_rec(puzzle, next_row_ix, next_col_ix)

    global metrics
    metrics.puzzle_solve_rec += 1
    if metrics.puzzle_solve_rec % METRIC_DISPLAY_INTERVAL == 0:
        metrics.display()

    for option in range(1, 10):
        puzzle[row_ix][col_ix] = option
        if blocks_is_valid(puzzle_collect_blocks(puzzle, block_ix)) and puzzle_solve_rec(puzzle, next_row_ix, next_col_ix):
            return puzzle
        puzzle[row_ix][col_ix] = 0
    return None


def best_path_next_step(puzzle: Puzzle) -> List[Tuple[int, int]]:
    blocks = sorted(range(9), key=lambda block_ix: len(
        remove_zeros(puzzle_collect_block(puzzle, block_ix))))
    rows = sorted(range(9), key=lambda row_ix: len(
        remove_zeros(puzzle[row_ix])))
    cols = sorted(range(9), key=lambda col_ix: len(
        remove_zeros([puzzle[i][col_ix] for i in range(9)])))
    best_path = []
    for row_ix in rows:
        for col_ix in cols:
            if puzzle[row_ix][col_ix] == 0:
                best_path.append((row_ix, col_ix))
    return sorted(best_path, key=lambda p: (blocks.index(get_block_index(p[0], p[1])), rows.index(p[0]), rows.index(p[1])))


def puzzle_solve_iterative(puzzle: Puzzle):
    stack = [(puzzle_copy(puzzle), 0, 0)]

    while len(stack) > 0:
        puzzle, row_ix, col_ix = stack.pop()
        if row_ix >= 9 or col_ix >= 9:
            break

        next_row_ix, next_col_ix = get_next_step(row_ix, col_ix)
        block_ix = get_block_index(row_ix, col_ix)

        if puzzle[row_ix][col_ix] != 0:
            stack.append((puzzle, next_row_ix, next_col_ix))
            continue

        metrics.puzzle_solve += 1
        if metrics.puzzle_solve % METRIC_DISPLAY_INTERVAL == 0:
            metrics.display()

        row = puzzle[row_ix]
        col = [puzzle[i][col_ix] for i in range(9)]
        block = puzzle_collect_block(puzzle, block_ix)

        options = set(range(1, 10)) - set(row) - set(col) - set(block)

        nexts = []
        for option in options:
            puzzle[row_ix][col_ix] = option
            nexts.append((puzzle_copy(puzzle), next_row_ix, next_col_ix))
            puzzle[row_ix][col_ix] = 0
        stack.extend(reversed(nexts))
    return puzzle


def puzzle_solve(puzzle_original: Puzzle):
    global metrics
    metrics = Metrics()
    metrics.start()
    # result = puzzle_solve_rec(puzzle_copy(puzzle_original))
    result = puzzle_solve_iterative(puzzle_copy(puzzle_original))
    metrics.end()
    metrics.display()
    return result


def puzzle_is_solution(puzzle: Puzzle, solution: Puzzle):
    return puzzle_is_complete(solution) and puzzle_is_valid(solution) and all(puzzle[i][j] == 0 or puzzle[i][j] == solution[i][j] for i in range(9) for j in range(9))


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
    print()


def puzzle_copy(puzzle: Puzzle) -> Puzzle:
    return [row.copy() for row in puzzle]


def run(puzzle_path, puzzle_solution_path=None):
    puzzle = puzzle_from_csv(puzzle_path)
    if not puzzle_is_valid(puzzle):
        print("ERROR: Puzzle is not valid")
        return
    print("INFO: Puzzle loaded")
    print("Puzzle: ")
    puzzle_display(puzzle)

    puzzle_solution = None
    if puzzle_solution_path:
        puzzle_solution = puzzle_from_csv(puzzle_solution_path)
        if not puzzle_is_solution(puzzle, puzzle_solution):
            print("ERROR: Puzzle solution is not valid")
            return
        print("INFO: Puzzle solution loaded")
        print("Puzzle solution: ")
        puzzle_display(puzzle_solution)

    puzzle_solution2 = puzzle_solve(puzzle)
    print()

    if puzzle_solution:
        if puzzle_solution == puzzle_solution2:
            print("Puzzle solution is valid and matches the provided solution")
        elif puzzle_is_solution(puzzle, puzzle_solution2):
            print("Puzzle solution is valid but does not match the provided solution")
        else:
            print("Puzzle solution is not valid")

    if puzzle_solution2 and not puzzle_is_solution(puzzle, puzzle_solution2):
        print("ERROR: Puzzle solution generated is not valid")

    print("Puzzle solution: ")
    puzzle_display(puzzle_solution2)

# puzzle_path = "puzzles/easy.csv"
# puzzle_solution_path = "puzzles/easy_solution_1.csv"


puzzle_path = "puzzles/hard_1.csv"
puzzle_solution_path = "puzzles/hard_1_solution.csv"


# puzzle_path = "puzzles/hard_2.csv"
# puzzle_solution_path = "puzzles/hard_2_solution.csv"

run(puzzle_path, puzzle_solution_path)
