from typing import List, Tuple

from .types import Cage, Puzzle


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

    def __str__(self):
        return 'RuleHorizontal'


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

    def __str__(self):
        return 'RuleVertical'


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

    def __str__(self):
        return 'RuleBlock'


class RuleAll(Rule):
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        return all(rule.apply(puzzle, x, y) for rule in self.rules)

    def __str__(self):
        return 'RuleAll({})'.format(', '.join(map(str, self.rules)))


class RuleBasic(Rule):
    def __init__(self):
        self.rules = RuleAll([RuleHorizontal(), RuleVertical(), RuleBlock()])

    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        return self.rules.apply(puzzle, x, y)

    def __str__(self):
        return 'RuleBasic'


class RuleCage(Rule):
    def __init__(self, cage: Cage):
        self.cage = cage

    def apply(self, puzzle: Puzzle, x: int, y: int) -> bool:
        if (x, y) in self.cage:
            for (cx, cy) in self.cage:
                if x == cx and y == cy:
                    continue
                if puzzle[cx][cy] == 0:
                    continue
                if puzzle[x][y] == puzzle[cx][cy]:
                    return False
        return True

    def __str__(self):
        return 'RuleCage({})'.format(self.cage)


class RuleConsecutivesOrtogonalAdjacents(Rule):
    def apply(self, puzzle: Puzzle, i: int, j: int) -> bool:
        if puzzle[i][j] == 0:
            return True

        values = []
        if puzzle[i][j] > 1:
            values.append(puzzle[i][j] - 1)
        if puzzle[i][j] < 9:
            values.append(puzzle[i][j] + 1)

        if i > 0 and puzzle[i - 1][j] in values:
            return False
        if i < 8 and puzzle[i + 1][j] in values:
            return False
        if j > 0 and puzzle[i][j - 1] in values:
            return False
        if j < 8 and puzzle[i][j + 1] in values:
            return False
        return True

    def __str__(self):
        return 'RuleConsecutivesOrtogonalAdjacents'


class RuleInfeasible(Rule):
    def __init__(self, rule: Rule):
        self.rule = rule
        self.count = 0
        self.iterations = 1

    def generate_options(self, puzzle: Puzzle) -> Tuple[Tuple[int, int], List[int]]:
        for i in range(9):
            for j in range(9):
                initial = puzzle[i][j]
                values = []
                for value in range(1, 10):
                    puzzle[i][j] = value
                    if self.rule.apply(puzzle, i, j):
                        values.append(value)
                    puzzle[i][j] = initial
                yield (i, j), values

    def apply(self, puzzle: Puzzle, _x: int, _y: int) -> bool:
        self.count += 1
        if self.count % self.iterations == 0:
            for _ij, values in self.generate_options(puzzle):
                if len(values) == 0:
                    return False
        return True


def rule_apply_puzzle(rule: Rule, puzzle: Puzzle) -> bool:
    for i in range(9):
        for j in range(9):
            if not rule.apply(puzzle, i, j):
                return False
    return True
