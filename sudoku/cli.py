import argparse
import asyncio
import concurrent.futures
import glob
import itertools
import os
import subprocess
import time
from pathlib import Path

import sudoku.solver_v2

from .collect_next_steps import (make_collect_valid_blocks,
                                 make_collect_valid_options,
                                 make_collect_valid_options_with_game,
                                 rule_from_game)
from .helpers import (check_puzzle_is_complete, check_puzzle_is_solution,
                      puzzle_display, puzzle_from_csv, puzzle_from_txt,
                      why_is_invalid)
from .logger import Logger
from .metrics import Metrics
from .next_step import (SEQUENCE_1, make_compute_next_step,
                        make_compute_next_step_block_column,
                        make_compute_next_step_block_row,
                        make_compute_next_step_heuristic1,
                        make_compute_next_step_heuristic2,
                        make_compute_next_step_sequence)
from .rules import rule_apply_puzzle
from .solver import Solver
from .types import Game


def cmd_run(args, **kwargs):
    print(f"CMD: '{' '.join(args)}'")
    subprocess.run(args, **kwargs)


def format_file(filepath):
    cmd_run(["python3", "-m", "autopep8", "--in-place", filepath], check=True)
    cmd_run(["python3", "-m", "isort", filepath], check=True)


async def format_files():
    files = itertools.chain(
        glob.glob("*.py"),
        glob.glob("sudoku/**/*.py", recursive=True)
    )
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as executor:
        for _ in executor.map(format_file, files):
            pass


def command_format_code(args):
    asyncio.run(format_files())


def interactive(solver, puzzle):
    show = True
    count = 0
    last_count = 0
    start_time = time.time()
    end_time = time.time()
    for i, (solution, row_ix, col_ix, stack) in enumerate(solver.solve_interative(puzzle)):
        if not show and i % 1000000 == 0:
            print(
                f'Iteration {i}: Stack size {len(stack)} Time {end_time - start_time} Coord ({row_ix}, {col_ix})')
        else:
            if count == 0:
                end_time = time.time()
                print(
                    f'Iteration {i}: Stack size {len(stack)} Time {end_time - start_time} Coord ({row_ix}, {col_ix})')
                puzzle_display(solution)

        if count == 0:
            new_count = input(">>> ").lower().strip()
            if new_count == "s" or new_count == "show":
                show = not show
                if show:
                    puzzle_display(solution)
                continue
            elif new_count == "q" or new_count == "quit":
                break
            elif new_count == "bp" or new_count == "breakpoint":
                import pdb
                pdb.set_trace()
            else:
                try:
                    count = int(new_count) - 1
                    last_count = count
                except BaseException:
                    count = last_count
        else:
            count -= 1
    return solution


def game_from_file(file_path: Path) -> Game:
    if file_path.suffix == ".csv":
        puzzle = puzzle_from_csv(file_path)
        rules = ["normal rules"]
        return Game(puzzle, [], rules)
    elif file_path.suffix == ".txt":
        return puzzle_from_txt(file_path)
    else:
        raise ValueError(f"Unknown file type: {file_path}")


def command_solve(args):
    game = game_from_file(args.puzzle_path)
    puzzle = game.puzzle

    print("Puzzle: ")
    puzzle_display(game.puzzle)
    print()

    if args.next_step == "base":
        next_step = make_compute_next_step(puzzle)
    elif args.next_step == "block_column":
        next_step = make_compute_next_step_block_column(puzzle)
    elif args.next_step == "block_row":
        next_step = make_compute_next_step_block_row(puzzle)
    elif args.next_step == "heuristic1":
        next_step = make_compute_next_step_heuristic1(puzzle)
    elif args.next_step == "heuristic2":
        next_step = make_compute_next_step_heuristic2(puzzle)
    elif args.next_step == "sequence1":
        next_step = make_compute_next_step_sequence(SEQUENCE_1)
    else:
        next_step = make_compute_next_step(puzzle)

    if len(game.rules) > 0:
        collect_next_steps = make_collect_valid_options_with_game(game)
    elif args.collect_next_steps == "valid_options":
        collect_next_steps = make_collect_valid_options()
    elif args.collect_next_steps == "valid_blocks":
        collect_next_steps = make_collect_valid_blocks()
    else:
        collect_next_steps = make_collect_valid_options()

    if args.solver_version == "v1":
        logger = Logger(args.logger_iterations)
        metrics = Metrics()
        solver = Solver(next_step, collect_next_steps, metrics, logger)

        metrics.start()
        logger.start()

        if args.interactive:
            solution = interactive(solver, puzzle)
        else:
            if args.solve_type == "recursive":
                solution = solver.solve_recursive(puzzle)
            elif args.solve_type == "iterative_bfs":
                # Not good
                solution = solver.solve_iterative_bfs(puzzle)
            elif args.solve_type == "threads":
                # Not so good
                solution = solver.solve_threads(puzzle)
            elif args.solve_type == "smart":
                solution = solver.solve_smart(puzzle)
            else:
                solution = solver.solve_iterative(puzzle)

        metrics.end()
        logger.end()

        if args.show_metrics:
            metrics.display()
            print()
    else:
        metrics = Metrics()
        metrics.start()
        solution = [[x for x in row] for row in puzzle]  # Copy puzzle

        solver = sudoku.solver_v2.PuzzleSolver(solution, next_step)
        solver.add_rule(sudoku.solver_v2.RuleHorizontal())
        solver.add_rule(sudoku.solver_v2.RuleVertical())
        solver.add_rule(sudoku.solver_v2.RuleBlock())

        solver.solve()
        metrics.end()

        if args.show_metrics:
            metrics.display()
            print()

    print("Puzzle Solution: ")
    puzzle_display(solution)

    if not solution or not check_puzzle_is_solution(puzzle, solution):
        print()
        print("ERROR: Puzzle solution is not valid")

    if args.solution_path:
        game_solution = game_from_file(Path(args.solution_path))
        print()
        if not check_puzzle_is_solution(game.puzzle, game_solution.puzzle):
            print("Puzzle solution: INVALID")
        elif solution == game_solution.puzzle:
            print("Puzzle solution: VALID + MATCH")
        else:
            print("Puzzle solution: VALID + NO MATCH")


def command_is_valid(args):
    if args.puzzle_path.suffix == ".csv":
        puzzle = puzzle_from_csv(args.puzzle_path)
        cages = []
        rules = ["normal rules"]
        game = Game(puzzle, cages, rules)
    elif args.puzzle_path.suffix == ".txt":
        game = puzzle_from_txt(args.puzzle_path)
    rule = rule_from_game(game)

    print("Puzzle:")
    puzzle_display(game.puzzle)
    print()
    print("Puzzle is valid:   ", rule_apply_puzzle(rule, game.puzzle))
    print("Puzzle is complete:", check_puzzle_is_complete(game.puzzle))


def command_why_invalid(args):
    puzzle = puzzle_from_csv(args.puzzle_path)
    print("Puzzle:")
    puzzle_display(puzzle)
    print()
    why_is_invalid(puzzle)


def get_parser():
    def command(func):
        name = func.__name__[len("command_"):].replace('_', '-')
        sb = subparsers.add_parser(name, help=func.__doc__)
        sb.set_defaults(func=func)
        return sb

    parser = argparse.ArgumentParser(description='Sudoku Solver')
    subparsers = parser.add_subparsers(dest="command", help='sub-command help')

    sb = command(command_solve)
    sb.add_argument('puzzle_path', help='Path to the puzzle CSV file',
                    type=Path)
    sb.add_argument('-i', '--interactive', action='store_true',
                    help='Interactive mode')
    sb.add_argument('--solver-version',
                    choices=["v1", "v2"], default="v1", help='Solver version')
    sb.add_argument('--solve-type',
                    choices=["recursive", "iterative", "iterative_bfs", "threads", "smart"], default="iterative", help='Solve type')
    sb.add_argument('--next-step',
                    choices=["base", "block_column", "block_row", "heuristic1", "heuristic2", "sequence1"], default="base", help='Next step')
    sb.add_argument('--collect-next-steps',
                    choices=["valid_options", "valid_blocks"], default="valid_options", help='Collect next steps')
    sb.add_argument('--logger-iterations', type=int, default=1e10,
                    help='Number of iterations to log')
    sb.add_argument('--show-metrics', action='store_true', help='Show metrics')
    sb.add_argument('--solution-path', help='Path to the solution CSV file')

    sb = command(command_is_valid)
    sb.add_argument(
        'puzzle_path', help='Path to the puzzle CSV file', type=Path)

    sb = command(command_why_invalid)
    sb.add_argument('puzzle_path', help='Path to the puzzle CSV file')

    sb = command(command_format_code)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
