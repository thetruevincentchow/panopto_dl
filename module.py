from typing import *


class ModuleTime:
    def __init__(self, start_year, end_year, sem):
        self.start_year = start_year
        self.end_year = end_year
        self.sem = sem

    def key(self):
        return (self.start_year, self.end_year, self.sem)

    def __lt__(self, other):
        return self.key() < other.key()

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    def __str__(self):
        return "AY%s/%s Sem %s" % (self.start_year, self.end_year, self.sem,)

    def __repr__(self):
        return "ModuleTime%r" % (self.key(),)


class ModuleInfo:
    def __init__(self, name, time):
        self.name = name
        self.time = time

    def key(self):
        return (self.name, self.time)

    def __hash__(self):
        return hash(self.key())

    def to_file_name(self):
        return "AY %s %s_Sem %s_%s" % (
            self.time.start_year,
            self.time.end_year,
            self.time.sem,
            self.name.replace("/", "-"),
        )

    def __str__(self):
        return "%s (%s)" % (self.name, self.time)

    def __repr__(self):
        return "ModuleInfo%r" % (self.key(),)
