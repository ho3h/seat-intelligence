"""T4 Trees (20 programs). Binary trees of u24 values.

Encoding (every program): a tree is Leaf or Node(left, value, right), where left and right are trees and value is a u24.
As a value: Leaf = (0,) and Node = (1, left, value, right). All arithmetic is mod 2^24 unless stated.
Terms used below: the root has depth 0; a "leaf node" is a Node whose left and right are both Leaf (the Leaf
constructor itself is the empty tree, not a leaf node); a BST is a tree where, at every Node, every value in its left
subtree is strictly smaller and every value in its right subtree is strictly larger than its value (so no duplicates).
"""
from collections import deque
from . import program
from ..types import u24, list_of, tup, tree_of, MASK

T = tree_of(u24)
L = list_of(u24)
M = MASK
BIG = MASK  # 16777215
S = list(range(0, 12))
TS = [90, 180]

TREE = ("A tree is Leaf or Node(left, value, right) (as a value: Leaf = (0,), Node = (1, left, value, right)), "
        "value a u24. ")
BSTD = ("A BST is a tree where at every Node all values in the left subtree are strictly smaller and all values in "
        "the right subtree strictly larger than the Node's value (no duplicates). ")

LEAF = (0,)
def N(l, v, r): return (1, l, v, r)
def one(v): return N(LEAF, v, LEAF)


# ---------------------------------------------------------------- pure helpers
def size(t): return 0 if t[0] == 0 else 1 + size(t[1]) + size(t[3])
def height(t): return 0 if t[0] == 0 else 1 + max(height(t[1]), height(t[3]))

def inorder(t, acc=None):
    acc = [] if acc is None else acc
    if t[0] == 1:
        inorder(t[1], acc); acc.append(t[2]); inorder(t[3], acc)
    return acc

def preorder(t, acc=None):
    acc = [] if acc is None else acc
    if t[0] == 1:
        acc.append(t[2]); preorder(t[1], acc); preorder(t[3], acc)
    return acc

def postorder(t, acc=None):
    acc = [] if acc is None else acc
    if t[0] == 1:
        postorder(t[1], acc); postorder(t[3], acc); acc.append(t[2])
    return acc

def level_order(t):
    out, q = [], deque([t])
    while q:
        u = q.popleft()
        if u[0] == 1:
            out.append(u[2]); q.append(u[1]); q.append(u[3])
    return out

def is_bst(t, lo=-1, hi=1 << 30):
    if t[0] == 0: return True
    v = t[2]
    return lo < v < hi and is_bst(t[1], lo, v) and is_bst(t[3], v, hi)

def mirror(t): return t if t[0] == 0 else N(mirror(t[3]), t[2], mirror(t[1]))

def map_add(a):
    k, t = a
    def go(u): return u if u[0] == 0 else N(go(u[1]), (u[2] + k) & M, go(u[3]))
    return go(t)

def depth_count(a):
    d, t = a
    def go(u, e):
        if u[0] == 0: return 0
        if e == d: return 1
        return go(u[1], e + 1) + go(u[3], e + 1)
    return go(t, 0)

def path_sums(t):
    out = []
    def go(u, s):
        if u[0] == 0: return
        s = (s + u[2]) & M
        if u[1][0] == 0 and u[3][0] == 0: out.append(s); return
        go(u[1], s); go(u[3], s)
    go(t, 0)
    return out

def max_path_sum(t): return max(path_sums(t), default=0)

def diameter(t):
    best = 0
    def h(u):
        nonlocal best
        if u[0] == 0: return 0
        a, b = h(u[1]), h(u[3])
        best = max(best, a + b)
        return 1 + max(a, b)
    h(t)
    return best

def fold_hash(t):
    if t[0] == 0: return 0
    return (2 * fold_hash(t[1]) + 3 * t[2] + 5 * fold_hash(t[3]) + 1) & M

def merge_add(a):
    x, y = a
    if x[0] == 0: return y
    if y[0] == 0: return x
    return N(merge_add((x[1], y[1])), (x[2] + y[2]) & M, merge_add((x[3], y[3])))

def min_max(t):
    vs = inorder(t)
    return (min(vs), max(vs)) if vs else (BIG, 0)

def bst_insert(a):
    x, t = a
    def go(u):
        if u[0] == 0: return one(x)
        if x < u[2]: return N(go(u[1]), u[2], u[3])
        if x > u[2]: return N(u[1], u[2], go(u[3]))
        return u
    return go(t)

def bst_delete_min(t):
    if t[0] == 0: return t
    if t[1][0] == 0: return t[3]
    return N(bst_delete_min(t[1]), t[2], t[3])

def bst_from_sorted(xs):
    def go(lo, hi):  # xs[lo:hi]
        if lo >= hi: return LEAF
        m = lo + (hi - lo - 1) // 2
        return N(go(lo, m), xs[m], go(m + 1, hi))
    return go(0, len(xs))

def bst_kth(a):
    k, t = a
    vs = inorder(t)
    return vs[k] if k < len(vs) else BIG

def bst_lca(a):
    x, y, t = a
    lo, hi = min(x, y), max(x, y)
    while True:
        v = t[2]
        if hi < v: t = t[1]
        elif lo > v: t = t[3]
        else: return v

def contains(t, x): return x in inorder(t)


# ---------------------------------------------------------------- generators
MODES = ("bal", "left", "right", "rand", "rand")

def _split(rng, n, mode):
    if mode == "bal": return (n - 1) // 2
    if mode == "left": return n - 1 if rng.random() < 0.85 else rng.randrange(n)
    if mode == "right": return 0 if rng.random() < 0.85 else rng.randrange(n)
    return rng.randrange(n)

def build(rng, n, mode, val):
    """n nodes; val() is called in in-order sequence."""
    if n == 0: return LEAF
    k = _split(rng, n, mode)
    l = build(rng, k, mode, val); v = val(); r = build(rng, n - 1 - k, mode, val)
    return N(l, v, r)

def rtree(rng, n, hi=100):
    return build(rng, n, rng.choice(MODES), lambda: rng.randrange(hi))

def rbst(rng, n):
    it = iter(sorted(rng.sample(range(max(100, 3 * n)), n)))
    return build(rng, n, rng.choice(MODES), lambda: next(it))



# ---------------------------------------------------------------- edges
E0 = LEAF
E1 = one(5)
EL = N(N(one(1), 2, LEAF), 3, LEAF)            # left chain 3 -> 2 -> 1
ER = N(LEAF, 1, N(LEAF, 2, one(3)))            # right chain 1 -> 2 -> 3
EB = N(N(one(1), 2, one(3)), 4, N(one(5), 6, one(7)))  # perfect BST 1..7
EX = N(one(BIG), 0, N(LEAF, BIG, LEAF))        # extreme values, not a BST
EZ = N(N(LEAF, 7, one(9)), 4, one(4))          # zigzag, duplicates
TE = [E0, E1, EL, ER, EB, EX, EZ]
BE = [E0, E1, EL, ER, EB, N(LEAF, 0, one(BIG))]  # BSTs


# ---------------------------------------------------------------- programs
program("t4_tree_size", "T4", TREE + "Output the number of Node constructors in the tree. Leaf gives 0.",
        T, u24, size, rtree, S, TS, edges=TE)

program("t4_tree_height", "T4", TREE + "Output the height: height(Leaf) = 0, height(Node(l, v, r)) = 1 + max(height(l), height(r)).",
        T, u24, height, rtree, S, TS, edges=TE)

program("t4_tree_min_max", "T4",
        TREE + "Output the pair (smallest value, largest value) over all Nodes. Leaf gives (16777215, 0).",
        T, tup(u24, u24), min_max, lambda r, n: rtree(r, n, 1000), S, TS, edges=TE)

program("t4_tree_inorder", "T4",
        TREE + "Output the list of values in in-order: inorder(Leaf) = [], inorder(Node(l, v, r)) = inorder(l) ++ [v] ++ inorder(r).",
        T, L, inorder, rtree, S, TS, edges=TE)

program("t4_tree_preorder", "T4",
        TREE + "Output the list of values in pre-order: pre(Leaf) = [], pre(Node(l, v, r)) = [v] ++ pre(l) ++ pre(r).",
        T, L, preorder, rtree, S, TS, edges=TE)

program("t4_tree_postorder", "T4",
        TREE + "Output the list of values in post-order: post(Leaf) = [], post(Node(l, v, r)) = post(l) ++ post(r) ++ [v].",
        T, L, postorder, rtree, S, TS, edges=TE)

program("t4_tree_level_order", "T4",
        TREE + "Output the list of values in breadth-first order: the root (depth 0) first, then all Nodes at depth 1, then "
        "depth 2, and so on; within one depth, Nodes appear left to right (a Node's left subtree before its right subtree, "
        "i.e. the order they occur in a pre-order walk). Leaf gives [].",
        T, L, level_order, rtree, S, TS, edges=TE)

program("t4_tree_mirror", "T4",
        TREE + "Output the mirror image: mirror(Leaf) = Leaf, mirror(Node(l, v, r)) = Node(mirror(r), v, mirror(l)).",
        T, T, mirror, rtree, S, TS, edges=TE)

program("t4_tree_map_add", "T4",
        TREE + "Input is (k, t). Output a tree of exactly the same shape as t where every value v is replaced by "
        "(v + k) mod 2^24.",
        tup(u24, T), T, map_add,
        lambda r, n: (r.choice([r.randrange(100), r.randrange(M + 1)]), rtree(r, n)), S, TS,
        edges=[(3, E0), (0, EB), (1, EX), (BIG, E1), (7, EZ)])

program("t4_tree_depth_count", "T4",
        TREE + "Input is (d, t). Output the number of Nodes at depth exactly d, where the root Node has depth 0 and the "
        "children Nodes of a Node at depth e have depth e + 1. Gives 0 if d is at least the height of t (including Leaf).",
        tup(u24, T), u24, depth_count,
        lambda r, n: (lambda t: (r.randrange(0, height(t) + 2), t))(r.choice([rtree(r, n), build(r, n, "bal", lambda: r.randrange(100))])),
        S, TS, edges=[(0, E0), (0, E1), (1, E1), (2, EB), (1, EB), (BIG, EB), (2, EL)])

program("t4_tree_path_sums", "T4",
        TREE + "A leaf node is a Node whose left and right are both Leaf. For every leaf node, the sum (mod 2^24) of the "
        "values of all Nodes on the path from the root down to that leaf node, inclusive. Output these sums as a list "
        "ordered by the leaf nodes from left to right (the order they are reached in a pre-order walk). Leaf gives [].",
        T, L, path_sums, rtree, S, TS, edges=TE)

program("t4_tree_max_path_sum", "T4",
        TREE + "A leaf node is a Node whose left and right are both Leaf. For every leaf node take the sum, mod 2^24, of "
        "the values of all Nodes on the path from the root down to that leaf node, inclusive; output the largest of these "
        "reduced sums. Leaf (empty tree) gives 0.",
        T, u24, max_path_sum, rtree, S, TS, edges=TE + [N(one(BIG), 1, one(3))])

program("t4_tree_diameter", "T4",
        TREE + "Output the diameter: the largest number of edges on a path between any two Nodes (edges join a Node to "
        "its non-Leaf children). Equivalently, the maximum over all Nodes of height(left) + height(right), where "
        "height(Leaf) = 0 and height(Node(l, v, r)) = 1 + max(height(l), height(r)). Leaf and a single Node give 0.",
        T, u24, diameter, rtree, S, TS, edges=TE)

program("t4_tree_fold_hash", "T4",
        TREE + "Output f(t) where f(Leaf) = 0 and f(Node(l, v, r)) = (2*f(l) + 3*v + 5*f(r) + 1) mod 2^24.",
        T, u24, fold_hash, lambda r, n: rtree(r, n, 1000), S, TS, edges=TE)

program("t4_tree_merge_add", "T4",
        TREE + "Input is (a, b), two trees. Output merge(a, b) where merge(Leaf, y) = y, merge(x, Leaf) = x, and "
        "merge(Node(l1, v1, r1), Node(l2, v2, r2)) = Node(merge(l1, l2), (v1 + v2) mod 2^24, merge(r1, r2)). "
        "(Overlay the two trees; where both have a Node the values add, elsewhere the existing subtree is kept unchanged.)",
        tup(T, T), T, merge_add,
        lambda r, n: (rtree(r, n // 2 + r.randrange(0, 2)), rtree(r, n - n // 2)), S, TS,
        edges=[(E0, E0), (E1, E0), (E0, EB), (EL, ER), (EB, EB), (EX, EZ), (one(BIG), one(1))])

program("t4_bst_insert", "T4",
        TREE + BSTD + "Input is (x, t) with t a BST. Output the BST after inserting x by the standard unbalanced method: "
        "insert(Leaf) = Node(Leaf, x, Leaf); at Node(l, v, r): if x < v recurse into l, if x > v recurse into r, if x = v "
        "return the Node unchanged (duplicates are ignored). All other Nodes are kept exactly as they are.",
        tup(u24, T), T, bst_insert,
        lambda r, n: (lambda t: (r.choice(inorder(t)) if n and r.random() < 0.3 else r.randrange(max(100, 3 * n)), t))(rbst(r, n)),
        S, TS, edges=[(4, E0), (5, E1), (9, E1), (0, E1), (4, EB), (8, EB), (0, EB), (BIG, EL)],
        pre=lambda a: is_bst(a[1]))

program("t4_bst_delete_min", "T4",
        TREE + BSTD + "Input is a BST. Output the tree with its smallest value removed: follow left children from the root "
        "to the first Node whose left is Leaf, and replace that Node by its right subtree; all other Nodes are kept exactly "
        "as they are. Leaf gives Leaf.",
        T, T, bst_delete_min, rbst, S, TS, edges=BE, pre=is_bst)

program("t4_bst_from_sorted", "T4",
        TREE + "Input is a strictly increasing list xs. Output the height-balanced BST build(xs): build([]) = Leaf; "
        "otherwise with n = len(xs) and m = (n - 1) // 2 (integer division, so for even n the root is the lower of the two "
        "middle elements), build(xs) = Node(build(xs[0..m-1]), xs[m], build(xs[m+1..n-1])). The left part thus gets "
        "(n - 1) // 2 elements and the right part n // 2.",
        L, T, bst_from_sorted, lambda r, n: sorted(r.sample(range(max(100, 3 * n)), n)), S, TS,
        edges=[[], [5], [1, 2], [1, 2, 3], [1, 2, 3, 4], [0, 7, 9, BIG]],
        pre=lambda xs: all(a < b for a, b in zip(xs, xs[1:])))

program("t4_bst_kth", "T4",
        TREE + BSTD + "Input is (k, t) with t a BST and k counting from 0. Output the k-th smallest value of t (the value at "
        "index k of the in-order list inorder(Leaf) = [], inorder(Node(l, v, r)) = inorder(l) ++ [v] ++ inorder(r)). "
        "Gives 16777215 if k >= the number of Nodes.",
        tup(u24, T), u24, bst_kth, lambda r, n: (r.randrange(0, n + 2), rbst(r, n)), S, TS,
        edges=[(0, E0), (0, E1), (1, E1), (0, EB), (6, EB), (3, EB), (7, EB), (2, ER), (BIG, EL)],
        pre=lambda a: is_bst(a[1]))

def _lca_gen(r, n):
    t = rbst(r, max(n, 1)); vs = inorder(t)
    return (r.choice(vs), r.choice(vs), t)
program("t4_bst_lca", "T4",
        TREE + BSTD + "Input is (x, y, t) with t a BST containing both x and y (x may equal y, and either may be larger). "
        "Output the value of their lowest common ancestor: starting at the root Node with value v, if both x and y are "
        "< v go to the left child, if both are > v go to the right child, otherwise output v.",
        tup(u24, u24, T), u24, bst_lca, _lca_gen, S, TS,
        edges=[(5, 5, E1), (1, 3, EB), (3, 1, EB), (1, 7, EB), (5, 7, EB), (6, 6, EB), (3, 1, ER), (1, 2, EL)],
        pre=lambda a: is_bst(a[2]) and contains(a[2], a[0]) and contains(a[2], a[1]))
