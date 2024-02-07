
from collections import defaultdict
from datetime import datetime


METRIC_DISPLAY_INTERVAL = 1e10  # 5000


class Metrics:
    def __init__(self) -> None:
        self.values = defaultdict(int)
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = datetime.now()

    def end(self):
        self.end_time = datetime.now()

    def collect(self, name):
        self.values[name] += 1
        if self.values[name] % METRIC_DISPLAY_INTERVAL == 0:
            self.display()

    def display(self):
        values = self.get_values()
        max_len = max(len(name) for name in values) + 1
        template = f"    {{name:<{max_len}}}: {{value}}"

        print("Metrics: ")
        for name, value in values.items():
            print(template.format(name=name, value=value))

    def get_values(self):
        values = dict(self.values)
        if self.end_time and self.start_time:
            values["Duration"] = self.end_time - self.start_time
        return values
