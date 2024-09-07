from typing import Optional

from .collect_next_steps import CollectNextSteps
from .helpers import puzzle_copy
from .logger import Logger
from .metrics import Metrics
from .next_step import NextStep
from .types import Puzzle


class Solver:
    def __init__(self, next_step: NextStep,
                 collect_next_steps: CollectNextSteps,
                 metrics: Metrics,
                 logger: Logger):
        self.next_step = next_step
        self.collect_next_steps = collect_next_steps
        self.metrics = metrics
        self.logger = logger

    def solve_recursive(self, puzzle: Puzzle) -> Optional[Puzzle]:
        def go(puzzle, row_ix, col_ix):
            if row_ix >= 9 or col_ix >= 9:
                return puzzle

            self.metrics.collect("Solve Recursive")
            self.logger.puzzle(puzzle)

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

            self.metrics.collect("Solve Iterative DFS")
            self.logger.puzzle(puzzle)

            next_row_ix, next_col_ix = self.next_step.next(row_ix, col_ix)
            if puzzle[row_ix][col_ix] != 0:
                stack.append((puzzle, next_row_ix, next_col_ix))
                continue

            stack.extend(self.collect_next_steps.collect(
                puzzle, row_ix, col_ix, next_row_ix, next_col_ix))

        return puzzle

    def solve_iterative_bfs(self, puzzle: Puzzle) -> Optional[Puzzle]:
        # TODO: Not working properly

        start = self.next_step.start
        stacks = [[] for _ in range(81)]

        stacks[stack_position(puzzle)].append(
            (puzzle_copy(puzzle), start[0], start[1]))

        found = True
        while found:
            found = False
            for k, stack in enumerate(stacks):
                if len(stack) == 0:
                    continue
                found = True

                puzzle, row_ix, col_ix = stack.pop()
                if row_ix >= 9 or col_ix >= 9:
                    break

                self.metrics.collect("Solve Iterative BFS")
                self.logger.puzzle(puzzle)

                next_row_ix, next_col_ix = self.next_step.next(row_ix, col_ix)
                if puzzle[row_ix][col_ix] != 0:
                    stack.append((puzzle, next_row_ix, next_col_ix))
                    continue

                stacks[stack_position(puzzle)].extend(self.collect_next_steps.collect(
                    puzzle, row_ix, col_ix, next_row_ix, next_col_ix))

        return puzzle


def stack_position(puzzle: Puzzle) -> int:
    return sum(cell != 0 for row in puzzle for cell in row)
