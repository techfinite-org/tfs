from datetime import datetime
import time
from tfs.profiler.stack import Stack

class Timer():
    def __init__(self):
        self.parent = None
        self.child = []
        self.name = None
        self.start_time = 0
        self.end_time = 0
        self.ctx = None

    def add(self, child):
        self.child.append(child)

    def start(self, name):
        self.name = name
        self.ctx = self.name
        if not Stack().is_empty():
            self.parent = Stack().peek()
            self.parent.add(self)
            if self.parent.ctx:
                self.ctx = str(self.parent.ctx) + ">" + str(self.name)
        self.start_time = round(time.time() * 1000)
        Stack().push(self)
        return self

    def end(self):
        if Stack().is_empty():
            raise Exception("Empty Stack")
        self.end_time = round(time.time() * 1000)
        while not Stack().is_empty():
            last = Stack().pop()
            if last.name == self.name:
                break

    def print(self, file_name):
        overall_time = self.end_time - self.start_time
        cumulative_time = 0
        for child in self.child:
            cumulative_time += child.print(file_name)
        self_time = overall_time - cumulative_time
        with open(f"{file_name}.txt", "a") as file:
            file.write(f"{self.ctx},{self.start_time},{self.end_time},{overall_time},{self_time}\n")
        print(f"{self.ctx},{self.start_time},{self.end_time},{overall_time},{self_time}")
        return overall_time





