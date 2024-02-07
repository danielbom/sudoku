from typing import Optional

from .collect_next_steps import CollectNextSteps
from .metrics import Metrics
from .next_step import NextStep
from .helpers import puzzle_copy
from .types import Puzzle


class Solver:
    def __init__(self, next_step: NextStep, collect_next_steps: CollectNextSteps, metrics: Metrics):
        self.next_step = next_step
        self.collect_next_steps = collect_next_steps
        self.metrics = metrics

    def solve_recursive(self, puzzle: Puzzle) -> Optional[Puzzle]:
        def go(puzzle, row_ix, col_ix):
            if row_ix >= 9 or col_ix >= 9:
                return puzzle

            self.metrics.collect("Solve Recursive")

            next_row_ix, next_col_ix = self.next_step.next(row_ix, col_ix)
            if puzzle[row_ix][col_ix] != 0:
                return go(puzzle, next_row_ix, next_col_ix)

            nexts = self.collect_next_steps.collect(
                puzzle, row_ix, col_ix, next_row_ix, next_col_ix)

            for next_puzzle, next_row_ix, next_col_ix in nexts:
                solution_puzzle = go(next_puzzle, next_row_ix, next_col_ix)
                if solution_puzzle:
                    return solution_puzzle

        start = self.next_step.start
        return go(puzzle, start[0], start[1])

    def solve_iterative(self, puzzle: Puzzle) -> Optional[Puzzle]:
        start = self.next_step.start
        stack = [(puzzle_copy(puzzle), start[0], start[1])]

        while len(stack) > 0:
            puzzle, row_ix, col_ix = stack.pop()
            if row_ix >= 9 or col_ix >= 9:
                break

            self.metrics.collect("Solve Iterative")

            next_row_ix, next_col_ix = self.next_step.next(row_ix, col_ix)
            if puzzle[row_ix][col_ix] != 0:
                stack.append((puzzle, next_row_ix, next_col_ix))
                continue

            stack.extend(self.collect_next_steps.collect(
                puzzle, row_ix, col_ix, next_row_ix, next_col_ix))

        return puzzle
