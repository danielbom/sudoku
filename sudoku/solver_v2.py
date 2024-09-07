import time
from typing import List, Tuple

from .helpers import puzzle_display, puzzle_from_txt
from .next_step import (NextStep, make_compute_next_step,
                        make_compute_next_step_block_column,
                        make_compute_next_step_block_row)
from .rules import (Rule, RuleBlock, RuleCage,
                    RuleConsecutivesOrtogonalAdjacents, RuleHorizontal,
                    RuleVertical)
from .types import Cage, Puzzle


class RuleInfeasible(Rule):
    def __init__(self, solver):
        self.solver = solver

        self.cages_map = {}
        for rule in solver.rules:
            if isinstance(rule, RuleCage):
                for cage in rule.cages:
                    self.cages_map[cage] = rule.cages

        self.block_map = {}
        for i in range(3):
            for j in range(3):
                block = []
                for x in range(3):
                    for y in range(3):
                        block.append((i * 3 + x, j * 3 + y))
                for cord in block:
                    self.block_map[cord] = block

        self.lines_map = {}
        for i in range(9):
            line = []
            for j in range(9):
                line.append((i, j))
            for cord in line:
                self.lines_map[cord] = line

        self.columns_map = {}
        for i in range(9):
            column = []
            for j in range(9):
                column.append((j, i))
            for cord in column:
                self.columns_map[cord] = column

    def generate_options(self):
        for i in range(9):
            for j in range(9):
                if self.solver.puzzle[i][j] == 0:
                    ij = (i, j)
                    values = set(range(1, 10)) - \
                        set([self.solver.puzzle[x][y] for x, y in self.block_map[ij]]) - \
                        set([self.solver.puzzle[x][y] for x, y in self.lines_map[ij]]) - \
                        set([self.solver.puzzle[x][y] for x, y in self.columns_map[ij]]) - \
                        set([self.solver.puzzle[x][y]
                            for x, y in self.cages_map.get(ij, [])])
                    yield ij, values

    def apply(self, _puzzle: Puzzle, _x: int, _y: int) -> bool:
        for ij, values in self.generate_options():
            if len(values) == 0:
                return False
        return True


class PuzzleSolver:
    def __init__(self, puzzle: Puzzle, next_step: NextStep):
        self.puzzle = puzzle
        self.next_step = next_step
        self.rules = []
        self.stack = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def check(self, x: int, y: int) -> bool:
        return all(rule.apply(self.puzzle, x, y) for rule in self.rules)

    def _next_xy(self, x: int, y: int) -> (int, int):
        return self.next_step.next(x, y)

    def _next_empty(self, x, y):
        while x < 9 and y < 9:
            if self.puzzle[x][y] == 0:
                break
            y += 1
            if y == 9:
                x += 1
                y = 0
        return (x, y)

    def solve_init(self):
        x, y = self._next_empty(0, 0)
        self.stack = [(x, y, 1)]

    def solve_next(self) -> bool:
        if not self.stack:
            return True

        x, y, value = self.stack.pop()

        if value == 10:
            self.puzzle[x][y] = 0
            return False

        if x == 9:
            self.stack = []
            return True

        self.puzzle[x][y] = value
        while not self.check(x, y) and value < 9:
            value += 1
            self.puzzle[x][y] = value

        self.stack.append((x, y, value + 1))

        if self.check(x, y):
            nx, ny = self._next_xy(x, y)
            nx, ny = self._next_empty(nx, ny)
            self.stack.append((nx, ny, 1))
        else:
            self.puzzle[x][y] = 0

        return False

    def solve(self) -> bool:
        self.solve_init()
        while not self.solve_next():
            pass


def make_compute_next_step_smart(solver: PuzzleSolver) -> NextStep:
    rule_infeasible = RuleInfeasible(solver)

    def next_step(_x: int, _y: int):
        options = [(j, i, len(values))
                   for (i, j), values in rule_infeasible.generate_options()]
        options.sort()
        return options[0][1], options[0][0]

    return NextStep(next_step)


if __name__ == '__main__':
    puzzle, cages = puzzle_from_txt('puzzles/cages.txt')

    next_step = make_compute_next_step(puzzle)  # Basic
    solver = PuzzleSolver(puzzle, next_step)

    solver.add_rule(RuleHorizontal())
    solver.add_rule(RuleVertical())
    solver.add_rule(RuleBlock())

    solver.add_rule(RuleConsecutivesOrtogonalAdjacents())
    for cage in cages:
        solver.add_rule(RuleCage(cage))

    solver.add_rule(RuleInfeasible(solver))

    solver.next_step = make_compute_next_step_smart(solver)
    solver.solve_init()
    start_time = time.time()
    end_time = time.time()
    running = True
    show = True
    count = 0
    last_count = 0
    i = 0
    while running:
        if not show and i % 1000000 == 0:
            print(f'Iteration {i}: Stack size {len(solver.stack)}')
        else:
            if count == 0:
                end_time = time.time()
                print(
                    f'Iteration {i}: Stack size {len(solver.stack)} Time {end_time - start_time}')
                puzzle_display(solver.puzzle)

        if count == 0:
            new_count = input(">>> ")
            start_time = time.time()
            if new_count == "show":
                show = not show
                if show:
                    puzzle_display(solver.puzzle)
                continue
            else:
                try:
                    count = int(new_count) - 1
                    last_count = count
                except BaseException:
                    count = last_count
        else:
            count -= 1

        solver.solve_next()
        i += 1

    puzzle_display(solver.puzzle)
