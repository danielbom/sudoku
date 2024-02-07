import argparse
import subprocess

from pathlib import Path

from .collect_next_steps import make_collect_valid_blocks, make_collect_valid_options
from .helpers import check_puzzle_is_complete, check_puzzle_is_solution, check_puzzle_is_valid, puzzle_display, puzzle_from_csv, why_is_invalid
from .metrics import Metrics
from .next_step import make_compute_next_step, make_compute_next_step_block_column, make_compute_next_step_block_row, make_compute_next_step_heuristic1, make_compute_next_step_heuristic2
from .solver import Solver


def run_cmd(cmd):
    print("CMD:", ' '.join(cmd))
    result = subprocess.run(
        cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)


def command_solve(args):
    puzzle = puzzle_from_csv(args.puzzle_path)
    print("Puzzle: ")
    puzzle_display(puzzle)
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
    else:
        next_step = make_compute_next_step(puzzle)

    if args.collect_next_steps == "valid_options":
        collect_next_steps = make_collect_valid_options()
    elif args.collect_next_steps == "valid_blocks":
        collect_next_steps = make_collect_valid_blocks()
    else:
        collect_next_steps = make_collect_valid_options()

    metrics = Metrics()
    solver = Solver(next_step, collect_next_steps, metrics)

    metrics.start()
    if args.solve_type == "recursive":
        solution = solver.solve_recursive(puzzle)
    else:
        solution = solver.solve_iterative(puzzle)
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
        puzzle_solution = puzzle_from_csv(args.solution_path)
        print()
        if not check_puzzle_is_solution(puzzle, puzzle_solution):
            print("Puzzle solution: INVALID")
        elif solution == puzzle_solution:
            print("Puzzle solution: VALID + MATCH")
        else:
            print("Puzzle solution: VALID + NO MATCH")


def command_is_valid(args):
    puzzle = puzzle_from_csv(args.puzzle_path)
    print("Puzzle:")
    puzzle_display(puzzle)
    print()
    print("Puzzle is valid:   ", check_puzzle_is_valid(puzzle))
    print("Puzzle is complete:", check_puzzle_is_complete(puzzle))


def command_why_invalid(args):
    puzzle = puzzle_from_csv(args.puzzle_path)
    print("Puzzle:")
    puzzle_display(puzzle)
    print()
    why_is_invalid(puzzle)


def command_format_code(args):
    for filepath in Path(".").glob("**/*.py"):
        run_cmd(["python3", "-m", "autopep8",
                "--in-place", "--verbose", str(filepath)])
        run_cmd(["python3", "-m", "isort", str(filepath)])


def get_parser():
    def command(func):
        name = func.__name__[len("command_"):].replace('_', '-')
        sb = subparsers.add_parser(name, help=func.__doc__)
        sb.set_defaults(func=func)
        return sb

    parser = argparse.ArgumentParser(description='Sudoku Solver')
    subparsers = parser.add_subparsers(dest="command", help='sub-command help')

    sb = command(command_solve)
    sb.add_argument('puzzle_path', help='Path to the puzzle CSV file')
    sb.add_argument(
        '--solve-type', choices=["recursive", "iterative"], default="iterative", help='Solve type')
    sb.add_argument('--next-step', choices=["base", "block_column", "block_row",
                    "heuristic1", "heuristic2"], default="base", help='Next step')
    sb.add_argument('--collect-next-steps', choices=[
                    "valid_options", "valid_blocks"], default="valid_options", help='Collect next steps')
    sb.add_argument('--show-metrics', action='store_true', help='Show metrics')
    sb.add_argument('--solution-path', help='Path to the solution CSV file')

    sb = command(command_is_valid)
    sb.add_argument('puzzle_path', help='Path to the puzzle CSV file')

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
