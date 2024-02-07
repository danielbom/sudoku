from sudoku import puzzle_display, puzzle_from_csv, puzzle_is_solution, puzzle_solve, puzzle_is_valid


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
