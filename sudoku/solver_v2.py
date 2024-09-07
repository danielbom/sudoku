import time
from typing import List, Tuple

from .next_step import (NextStep, make_compute_next_step,
                        make_compute_next_step_block_column,
                        make_compute_next_step_block_row)
from .types import Puzzle

Cage = Tuple[int, int]


class Rule:
    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        pass


class RuleHorizontal(Rule):
    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        for i in range(9):
            if i == y:
                continue
            if puzzle[x][i] == 0:
                continue
            if puzzle[x][i] == puzzle[x][y]:
                return False
        return True


class RuleVertical(Rule):
    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        for i in range(9):
            if i == x:
                continue
            if puzzle[i][y] == 0:
                continue
            if puzzle[i][y] == puzzle[x][y]:
                return False
        return True


class RuleBlock(Rule):
    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        xx = x // 3 * 3
        yy = y // 3 * 3
        for i in range(3):
            for j in range(3):
                nx = xx + i
                ny = yy + j
                if nx == x and ny == y:
                    continue
                if puzzle[nx][ny] == 0:
                    continue
                if puzzle[nx][ny] == puzzle[x][y]:
                    return False
        return True


class RuleCages(Rule):
    def __init__(self, cages: List[Cage]):
        if len(cages) > 9:
            raise ValueError('Too many cages')
        if len(cages) < 1:
            raise ValueError('Too few cages')
        if len(cages) != len(set(cages)):
            raise ValueError('Duplicate cages')
        self.cages = cages

    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        if (x, y) in self.cages:
            for (cx, cy) in self.cages:
                if x == cx and y == cy:
                    continue
                if puzzle[cx][cy] == 0:
                    continue
                if puzzle[x][y] == puzzle[cx][cy]:
                    return False
        return True


class RuleConsecutivesOrtogonalAdjacents(Rule):
    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        value = puzzle[x][y]

        if value > 1:
            if x > 0 and puzzle[x - 1][y] == value - 1:
                return False
            if x < 8 and puzzle[x + 1][y] == value - 1:
                return False
            if y > 0 and puzzle[x][y - 1] == value - 1:
                return False
            if y < 8 and puzzle[x][y + 1] == value - 1:
                return False
        if value < 9:
            if x > 0 and puzzle[x - 1][y] == value + 1:
                return False
            if x < 8 and puzzle[x + 1][y] == value + 1:
                return False
            if y > 0 and puzzle[x][y - 1] == value + 1:
                return False
            if y < 8 and puzzle[x][y + 1] == value + 1:
                return False

        return True


class RuleInfeasible(Rule):
    def __init__(self, solver):
        self.solver = solver

        self.cages_map = {}
        for rule in solver.rules:
            if isinstance(rule, RuleCages):
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

    def show(self):
        print('-------------------------')
        for x in range(9):
            print(end='| ')
            for y in range(9):
                if solver.puzzle[x][y] == 0:
                    print('.', end=' ')
                else:
                    print(solver.puzzle[x][y], end=' ')
                if y % 3 == 2:
                    print('| ', end='')
            print()
            if x % 3 == 2:
                print('-------------------------')
        print()


def make_compute_next_step_smart(solver: PuzzleSolver) -> NextStep:
    rule_infeasible = RuleInfeasible(solver)

    def next_step(_x: int, _y: int):
        options = [(j, i, len(values))
                   for (i, j), values in rule_infeasible.generate_options()]
        options.sort()
        return options[0][1], options[0][0]

    return NextStep(next_step)


def parse_puzzle(filename: str) -> (Puzzle, List[List[Cage]]):
    puzzle = []
    cages = []
    with open(filename) as f:
        _ = f.readline()  # puzzle:
        for _ in range(9):
            line = f.readline().strip()
            puzzle.append([int(x.strip()) for x in line.split(',')])
        _ = f.readline()  # cages:
        while True:
            line = f.readline().strip()
            if not line:
                break
            cages.append([
                tuple(map(int, xs.strip().split(',')))
                for xs in line.split(';')
            ])
    return puzzle, cages


if __name__ == '__main__':
    puzzle, cages = parse_puzzle('puzzles/cages.txt')

    next_step = make_compute_next_step(puzzle)  # Basic
    solver = PuzzleSolver(puzzle, next_step)

    solver.add_rule(RuleHorizontal())
    solver.add_rule(RuleVertical())
    solver.add_rule(RuleBlock())

    solver.add_rule(RuleConsecutivesOrtogonalAdjacents())
    for cage in cages:
        solver.add_rule(RuleCages(cage))

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
                solver.show()

        if count == 0:
            new_count = input(">>> ")
            start_time = time.time()
            if new_count == "show":
                show = not show
                if show:
                    solver.show()
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

    solver.show()
