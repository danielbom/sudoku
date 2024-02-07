from collections import defaultdict


def check(matrix, value, x, y):
    for i in range(9):
        if i != y and matrix[x][i] == value:  # Line check
            return False
        if i != x and matrix[i][y] == value:  # Column check
            return False

    inc_x = (x // 3) * 3
    inc_y = (y // 3) * 3
    for i in range(3):        # Quad check
        for j in range(3):
            if not (i + inc_x == x and j + inc_y == y):
                if matrix[i + inc_x][j + inc_y] == value:
                    return False
    return True


def sudoku_solver(matrix):
    checker = defaultdict(set)

    def update_checker(x, y):
        values = checker[x, y]
        if len(values) == 1:
            value = values.pop()
            matrix[i][j] = value
            for k in range(i):
                checker[i, k].discard(value)
                update_checker(i, k)
            for k in range(j):
                checker[k, j].discard(value)
                update_checker(k, j)

    for i, line in enumerate(matrix):
        for j, elem in enumerate(line):
            if matrix[i][j] == 0:
                for x in range(1, 10):
                    if check(matrix, x, i, j):
                        checker[i, j].add(x)

    quads = {}
    for x in range(3):
        xx = x * 3
        for y in range(3):
            yy = y * 3
            quads[x, y] = checker[x, y]
            for i in range(3):
                for j in range(3):
                    quads[x, y] = checker[xx + i,
                                          yy + j].difference(quads[x, y])
            if not quads[x, y]:
                del quads[x, y]
            else:
                for i in range(3):
                    for j in range(3):
                        for value in quads[x, y]:
                            if value in checker[xx + i, yy + j]:
                                matrix[xx + i][yy + j] = value

    order = sorted(checker.items(), key=lambda x: len(x[1]))

    print(*list(checker.items()), sep="\n")
    print()
    print(*list(quads.items()), sep="\n")

    return matrix


puzzle = [[0, 0, 6, 1, 0, 0, 0, 0, 8],
          [0, 8, 0, 0, 9, 0, 0, 3, 0],
          [2, 0, 0, 0, 0, 5, 4, 0, 0],
          [4, 0, 0, 0, 0, 1, 8, 0, 0],
          [0, 3, 0, 0, 7, 0, 0, 4, 0],
          [0, 0, 7, 9, 0, 0, 0, 0, 3],
          [0, 0, 8, 4, 0, 0, 0, 0, 6],
          [0, 2, 0, 0, 5, 0, 0, 8, 0],
          [1, 0, 0, 0, 0, 2, 5, 0, 0]]

res = sudoku_solver(puzzle)

print(*res, sep="\n")
