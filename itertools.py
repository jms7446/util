
def str_findall(ptn, s):
    idx = s.find(ptn)
    while idx != -1:
        yield idx
        idx = s.find(ptn, idx + 1)


def iter_pair_in_order(xs, ys):
    for x in xs:
        for y in ys:
            if x < y:
                yield x, y


class BFSStack:
    def __init__(self, starts=None, step=0):
        if starts:
            self.stack = starts[:]
        else:
            self.stack = []
        self.step = step

    def next_step_iter(self):
        while self.stack:
            self.step += 1
            stack = self.stack
            self.stack = []
            yield self.step, stack

    def append(self, v):
        self.stack.append(v)

    def __repr__(self):
        return f'BFSStack({self.stack}, {self.step})'


class Direction:
    def __init__(self, dir_type, R, C):
        if dir_type == 4:
            self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        elif dir_type == 8:
            self.directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        else:
            raise Exception(f'Unknown dir_type: {dir_type}')
        self.R = R
        self.C = C

    def iter_next(self, point):
        pr, pc = point
        for dr, dc in self.directions:
            r, c = pr + dr, pc + dc
            if 0 <= r < self.R and 0 <= c < self.C:
                yield r, c
