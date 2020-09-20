
from operator import add


class SegmentTree:
    def __init__(self, xs, acc_func=add, init=0):
        def build(v, il, ir):
            if il == ir:
                self.tree[v] = xs[il]
            else:
                im = (il + ir) // 2
                self.tree[v] = self.acc_func(build(v * 2 + 1, il, im), build(v * 2 + 2, im + 1, ir))
            return self.tree[v]

        self.acc_func = acc_func
        self.init = init
        self.n = len(xs)
        self.tree = [0] * (self.n * 4)   # rough max
        build(0, 0, self.n - 1)

    def get_range_value(self, left, right):
        def get_value(v, il, ir):
            if il >= left and ir <= right:
                return self.tree[v]
            elif il > right or ir < left:
                return self.init
            else:
                im = (il + ir) // 2
                return self.acc_func(get_value(v * 2 + 1, il, im), get_value(v * 2 + 2, im + 1, ir))
        return get_value(0, 0, self.n - 1)

    def update(self, idx, val):
        def _update(v, il, ir):
            if il == idx and ir == idx:
                self.tree[v] = val
            elif il <= idx <= ir:
                im = (il + ir) // 2
                self.tree[v] = self.acc_func(_update(v * 2 + 1, il, im), _update(v * 2 + 2, im + 1, ir))
            return self.tree[v]
        _update(0, 0, self.n - 1)
