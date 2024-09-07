from datetime import datetime

from .helpers import puzzle_display


class Logger:
    def __init__(self, interval=1_000) -> None:
        self.count = 0
        self.interval = interval
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = datetime.now()

    def end(self):
        self.end_time = datetime.now()

    def puzzle(self, puzzle):
        self.count += 1
        if self.count % self.interval == 0:
            self.display(puzzle)
    
    def info(self, message):
        print(f"Logger: {message}")

    def display(self, puzzle):
        current_time = datetime.now()
        print(
            f"Logger: {self.count} iterations in {current_time - self.start_time}")
        puzzle_display(puzzle)
