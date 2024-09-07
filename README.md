py -m autopep8 sudoku.py -i -v
py -m autopep8 cli.py -i -v
py -m autopep8 experiment.py -i -v

# Puzzle: easy.csv

```bash
py ./cli.py solve ./puzzles/easy.csv --show-metrics --next-step heuristic2 --solve-type recursive --collect-next-steps valid_blocks --solution-path ./puzzles/easy_solution_1.csv
```

Metrics: 
    Solve Recursive : 1426
    Duration        : 0:00:00.116760

# Puzzle: hard_1.csv

```bash
py ./cli.py solve ./puzzles/hard_1.csv --show-metrics --next-step heuristic2 --solve-type recursive --collect-next-steps valid_blocks --solution-path ./puzzles/hard_1_solution.csv
```

Metrics: 
    Solve Recursive : 1058
    Duration        : 0:00:00.086665

```bash
py ./cli.py solve ./puzzles/hard_1.csv --show-metrics --next-step heuristic1 --solve-type iterative --collect-next-steps valid_options --solution-path ./puzzles/hard_1_solution.csv
```

Metrics: 
    Solve Iterative : 11350
    Duration        : 0:00:00.063643

# Puzzle: hard_2.csv

```bash
py ./cli.py solve ./puzzles/hard_2.csv --show-metrics --next-step heuristic1 --solve-type iterative --collect-next-steps valid_options --solution-path ./puzzles/hard_2_solution.csv
```

Metrics:
    Solve Iterative : 213
    Duration        : 0:00:00.000999

# Puzzle: cages.txt

```bash
py .\cli.py solve .\puzzles\cages.txt --show-metrics --logger-iterations 100000
```

Metrics: 
    Solve Iterative DFS : 164686753
    Duration            : 2:10:18.972162
