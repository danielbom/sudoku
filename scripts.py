import argparse
import asyncio
import concurrent.futures
import glob
import itertools
import os
import subprocess
from pathlib import Path


def cmd_run(args, **kwargs):
    print(f"CMD: '{' '.join(args)}'")
    subprocess.run(args, **kwargs)


def format_file(filepath):
    cmd_run(["autopep8", "--in-place", "--aggressive", filepath], check=True)
    cmd_run(["isort", filepath], check=True)


async def format_files():
    files = itertools.chain(
        glob.glob("*.py"),
        glob.glob("sudoku/**/*.py", recursive=True),
        glob.glob("references/**/*.py", recursive=True)
    )
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as executor:
        for _ in executor.map(format_file, files):
            pass


async def command_format(args: argparse.Namespace) -> None:
    await format_files()


async def command_check_types(_args: argparse.Namespace) -> None:
    cmd_run(["mypy", "."])


def get_parser():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command")

    sp = subparser.add_parser("format", help="Format python files")
    sp.set_defaults(func=command_format)

    sp = subparser.add_parser("check-types", help="Check types with mypy")
    sp.set_defaults(func=command_check_types)

    return parser


async def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    else:
        await args.func(args)


if __name__ == "__main__":
    asyncio.run(main())
