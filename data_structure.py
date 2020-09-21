
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


################################################################################
# KMP
################################################################################

class KMP:
    def __init__(self, ptn):
        self.ptn = ptn
        self.table = self.make_partial_match_table(ptn)

    @staticmethod
    def make_partial_match_table(ptn):
        table = [0] * len(ptn)
        cnd = 0
        for pos in range(1, len(ptn)):
            while cnd > 0 and ptn[pos] != ptn[cnd]:
                cnd = table[cnd - 1]
            if ptn[pos] == ptn[cnd]:
                cnd += 1
                table[pos] = cnd
        return table

    def search(self, in_str):
        ptn = self.ptn
        table = self.table
        len_ptn_minus1 = len(ptn) - 1
        j = 0
        for i, c in enumerate(in_str):
            while j > 0 and c != ptn[j]:
                j = table[j-1]
            if c == ptn[j]:
                if j == len_ptn_minus1:
                    yield i - len(ptn) + 1
                    j = table[j]
                else:
                    j += 1

################################################################################


################################################################################
# Tree
################################################################################

class TreeNode:
    def __init__(self, value, parent=None, children=None):
        self.value = value
        self.parent = parent
        self.children = children or []

    def __repr__(self):
        root_rep = ', root' if self.parent is None else ''
        return f'TreeNode({self.value}, #{len(self.children)}{root_rep})'


class Tree:
    def __init__(self, root: TreeNode):
        self.root = root

    @classmethod
    def from_values_and_edges(cls, values, edges, root_idx=0):
        nodes = [TreeNode(value) for value in values]
        for n1, n2 in edges:
            nodes[n1].children.append(nodes[n2])
            nodes[n2].children.append(nodes[n1])

        root = nodes[root_idx]
        stack = [root]
        while stack:
            node = stack.pop()
            for child in node.children:
                child.parent = node
                child.children.remove(node)
                if child.children:
                    stack.append(child)
        return cls(root)

    def iter_preorder(self):
        stack = [self.root]
        while stack:
            node = stack.pop()
            yield node
            sorted_children = sorted(node.children, key=lambda x: x.value, reverse=True)
            for child in sorted_children:
                stack.append(child)

################################################################################
