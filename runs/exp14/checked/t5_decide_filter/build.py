"""Build: t5_decide_filter
Input: (tau, cands): tau is an integer threshold 0..1000, cands is a list of (u, v, score) triples
Output: filtered triples with score >= tau, in original order
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, LIST, TUP, HOLE

def build():
    P = Program()

    # Triple type: (u (v score))
    TRIPLE = TUP(NUM, NUM, NUM)

    # Stream walker: walk the input list, filtering as we go
    # State: (tau, output_value, output_hole)
    # - tau: the threshold
    # - output_value: the wire to the result list (created by d.hole)
    # - output_hole: the current hole to fill with cons cells

    def step(d, tau, out_val, hole, u, v, score):
        """Process one triple: check if score >= tau, conditionally add to output"""
        # Elements are already split from the tuple elem=TRIPLE

        # tau is needed twice: in the comparison and passed to branches
        tau1, tau2 = d.fanout(tau, 2)

        # score is needed twice: in the comparison and in the reconstruction
        score1, score2 = d.fanout(score, 2)

        # Check if score >= tau
        # We need: score >= tau, which is equivalent to NOT(score < tau)
        lt = d.op(score1, "<", tau1)  # 1 if score < tau, 0 otherwise
        ge = d.op(lt, "^", 1)         # flip: 1 if score >= tau, 0 otherwise

        # Reconstruct the triple for potential output
        reconstructed = (u, (v, score2))

        # Conditionally add to output using d.branch
        # if ge != 0: add to list, else: skip
        # We need to pass tau and out_val through the branch
        def add(b, cm1, tau_inner, out_val_inner, hole_inner, triple_inner):
            """Add triple to output list (ge > 0)"""
            b.erase(cm1)  # cm1 is ge-1 (unused in this branch)
            new_hole = b.fill_cons(hole_inner, triple_inner)
            return tau_inner, out_val_inner, new_hole

        def skip(b, tau_inner, out_val_inner, hole_inner, triple_inner):
            """Skip this triple (ge == 0)"""
            b.erase(triple_inner)
            return tau_inner, out_val_inner, hole_inner

        return d.branch(ge, skip, add, tau2, out_val, hole, reconstructed)

    def fin(d, tau, out_val, hole):
        """Finalize: close the output list with nil"""
        d.erase(tau)  # tau is no longer needed
        d.fill(hole, d.nil(TRIPLE))  # close the hole with an empty list
        return out_val  # return the value (now fully constructed)

    w = P.stream("w", step, fin,
                 state=[("tau", NUM), ("out_val", LIST(TRIPLE)), ("hole", HOLE(LIST(TRIPLE)))],
                 elem=TRIPLE)

    def prog(d, tau, cands):
        """Main entry: filter the candidates"""
        # Create initial output list hole
        out_val, out_hole = d.hole(LIST(TRIPLE))

        # Walk the list with the stream
        result = d.call(w, list=cands, init=(tau, out_val, out_hole))

        return result

    P.prog("t5_decide_filter", prog)
    return P

if __name__ == "__main__":
    P = build()
    path = os.path.join(D, "net.hvm")
    P.write(path)
    print("wrote", path)
