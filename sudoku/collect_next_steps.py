from typing import List, Tuple

from .helpers import (cage_assert, check_blocks_is_valid, collect_puzzle_block,
                      collect_puzzle_blocks, compute_block_index, puzzle_copy)
from .rules import (RuleAll, RuleBasic, RuleCage,
                    RuleConsecutivesOrtogonalAdjacents, RuleInfeasible)
from .types import Cage, Game, Puzzle


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


def rule_from_game(game: Game):
    rules = []
    infeasible = False
    for name in game.rules:
        if name == "normal rules":
            rules.append(RuleBasic())
        elif name == "unique cages":
            for cage in game.cages:
                cage_assert(cage)
                rules.append(RuleCage(cage))
        elif name == "no consecutive digits in ortogonal adjacent":
            rules.append(RuleConsecutivesOrtogonalAdjacents())
        elif name == "infeasible":
            infeasible = True
        else:
            raise ValueError(f"Unknown rule: {name}")

    if infeasible:
        rules.append(RuleInfeasible(RuleAll(rules.copy())))

    return RuleAll(rules)


def collect_valid_options_with_game2(game: Game):
    def all_options(puzzle: Puzzle, row_ix: int, col_ix: int) -> List[int]:
        return list(range(1, 10))

    def row_options(puzzle: Puzzle, row_ix: int, col_ix: int) -> List[int]:
        return set(puzzle[row_ix])

    def col_options(puzzle: Puzzle, row_ix: int, col_ix: int) -> List[int]:
        return set([puzzle[i][col_ix] for i in range(9)])

    def block_options(puzzle: Puzzle, row_ix: int, col_ix: int) -> List[int]:
        return set(collect_puzzle_block(puzzle, compute_block_index(row_ix, col_ix)))

    def make_cage_options(cage: Cage):
        def cage_options(puzzle: Puzzle, row_ix: int, col_ix: int) -> List[int]:
            if (row_ix, col_ix) in cage:
                return set([puzzle[i][j] for i, j in cage])
            return set()
        return cage_options

    def no_consecutive_digits_in_ortogonal_adjacent(puzzle: Puzzle, row_ix: int, col_ix: int) -> List[int]:
        values = []
        if row_ix > 0:
            values.append(puzzle[row_ix - 1][col_ix])
        if row_ix < 8:
            values.append(puzzle[row_ix + 1][col_ix])
        if col_ix > 0:
            values.append(puzzle[row_ix][col_ix - 1])
        if col_ix < 8:
            values.append(puzzle[row_ix][col_ix + 1])
        values = [v for v in values if 1 <= v <= 9]
        options = []
        for x in values:
            if x > 0:
                options.append(x - 1)
            if x < 9:
                options.append(x + 1)
        return set(options)

    collectors_aditives = [all_options]
    collectors_substractives = []
    infeasible = False
    for name in game.rules:
        if name == "normal rules":
            collectors_substractives.extend([
                row_options, col_options, block_options])
        elif name == "unique cages":
            for cage in game.cages:
                cage_assert(cage)
                collectors_substractives.append(make_cage_options(cage))
        elif name == "no consecutive digits in ortogonal adjacent":
            collectors_substractives.append(
                no_consecutive_digits_in_ortogonal_adjacent)
            pass
        elif name == "infeasible":
            infeasible = True
        else:
            raise ValueError(f"Unknown rule: {name}")

    def collect(puzzle: Puzzle,
                row_ix: int, col_ix: int,
                next_row_ix: int, next_col_ix: int) -> List[Tuple[Puzzle, int, int]]:
        options = set()
        for collector in collectors_aditives:
            options.update(collector(puzzle, row_ix, col_ix))
        for collector in collectors_substractives:
            options -= collector(puzzle, row_ix, col_ix)
        nexts = []
        for option in options:
            puzzle[row_ix][col_ix] = option
            nexts.append((puzzle_copy(puzzle), next_row_ix, next_col_ix))
            puzzle[row_ix][col_ix] = 0
        nexts.reverse()
        return nexts
    return collect


def collect_valid_options_with_game1(game: Game):
    rule = rule_from_game(game)

    def collect(puzzle: Puzzle,
                row_ix: int, col_ix: int,
                next_row_ix: int, next_col_ix: int) -> List[Tuple[Puzzle, int, int]]:
        nexts = []
        for option in range(1, 10):
            puzzle[row_ix][col_ix] = option
            if rule.apply(puzzle, row_ix, col_ix):
                nexts.append((puzzle_copy(puzzle), next_row_ix, next_col_ix))
            puzzle[row_ix][col_ix] = 0
        nexts.reverse()
        return nexts

    return collect


def make_collect_valid_options_with_game(game: Game):
    # 700000 iterations in 30s
    # return CollectNextSteps(collect_valid_options_with_game1(game))
    # 2000000 iterations in 30s
    return CollectNextSteps(collect_valid_options_with_game2(game))
