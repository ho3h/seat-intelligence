#!/usr/bin/env python3
"""
Build the HVM2 net for t5_decide_normalise using the checked glue API.

Algorithm:
1. Stream through input list of triples (u, v, score)
2. Normalize each pair to (min(u,v), max(u,v))
3. Build a trie indexed by composite key: u * 2^12 + v
4. Store max score for each normalized pair
5. Use fold to convert trie back to sorted (u, v, score) triples
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(D), '..', '..', '..'))
from genome.lib.glue import Program, GlueError, NUM, DEPTH, ANY, LIST, TRIE, TUP, HOLE, EDGE, WEDGE, ADJ, INF


def build():
    P = Program()
    lg = P.lg()

    # Primitives
    zeros = P.const_trie("z0", 0)
    max_update = P.update("dmax", "max")

    L_KEY = 12  # Bit shift for composite key

    def step(d, L, h, u, v, score):
        """Process one triple: normalize and update trie"""
        L1, L2 = d.fanout(L, 2)
        u1, u2, u3 = d.fanout(u, 3)
        v1, v2, v3 = d.fanout(v, 3)

        # u < v: min=u, max=v; else: min=v, max=u
        cond = d.op(u1, "<", v1)
        sel = d.select(cond, (u2, v2), (v3, u3))
        min_u, max_u = d.split(sel)

        # Composite key: min_u + (max_u << L_KEY)
        # Low L_KEY bits hold min_u, high bits hold max_u
        shifted = d.op(max_u, "<<", L_KEY)
        key = d.op(min_u, "+", shifted)

        # Update trie with max score
        h2 = d.call(max_update, t=h, k=key, L=L1, P=score)

        return L2, h2

    def fin(d, L, h):
        d.erase(L)
        return h

    # Create fold leaf function
    def decode_leaf(d, score, i, acc):
        """Decode composite key and build output triple"""
        i1, i2 = d.fanout(i, 2)
        score1, score2 = d.fanout(score, 2)

        # Decompose key: min_u = key & ((1<<12)-1), max_u = key >> 12
        min_u = d.op(i1, "&", (1 << L_KEY) - 1)
        max_u = d.op(i2, ">>", L_KEY)

        # Branch on score: if score > 0 cons the triple, else return acc unchanged
        def zero_branch(b, acc_arg, min_u_arg, max_u_arg, score_arg):
            """score == 0: skip this entry"""
            b.erase(min_u_arg)
            b.erase(max_u_arg)
            b.erase(score_arg)
            return acc_arg

        def nonzero_branch(b, s_minus_1, acc_arg, min_u_arg, max_u_arg, score_arg):
            """score > 0: cons the normalized triple (min_u, max_u, score)"""
            b.erase(s_minus_1)
            return b.cons((min_u_arg, max_u_arg, score_arg), acc_arg)

        return d.branch(score1, zero_branch, nonzero_branch, acc, min_u, max_u, score2)

    fold = P.fold("fold", decode_leaf, acc=LIST(TUP(NUM, NUM, NUM)), index=True)
    w = P.stream("w", step, fin, state=[("L", DEPTH), ("h", TRIE(NUM))], elem=TUP(NUM, NUM, NUM))

    def prog(d, input_list):
        # Input is a list of triples: list[(u, v, score)]
        # Output is a sorted list of deduplicated triples with max scores

        # Use depth 14 for the trie (2^14 = 16384 leaves)
        # Composite key: min_u + (max_u << 12) for pairs normalized to (min, max)
        # Smaller depth means faster fold but less storage for large inputs
        L = d.call(lg, x=16383)  # lg(2^14 - 1) = 14
        L1, L2, L3 = d.fanout(L, 3)

        # Stream through input to build trie of max scores
        # init state: (L, empty_trie)
        init_trie = d.call(zeros, L=L1)
        H = d.call(w, list=input_list, init=(L2, init_trie))

        # H is the trie of max scores
        # Fold the trie to create sorted output list
        result = d.call(fold, t=H, L=L3, base=0, acc=d.nil())

        return result

    P.prog("t5_decide_normalise", prog)
    return P


if __name__ == "__main__":
    p = build()
    output_path = os.path.join(D, "net.hvm")
    try:
        p.write(output_path)
        print(f"Successfully wrote {output_path}")
    except GlueError as e:
        print(f"GlueError: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
