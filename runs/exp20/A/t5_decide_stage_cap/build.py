#!/usr/bin/env python3
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, LIST, TUP, WEDGE

P = Program()

def prog(d, tau, cap, cands):
    def step(d, tau_v, cap_v, pairs, deferred_cnt, staged_cnt, u, v, score):
        tau_a, tau_b = d.fanout(tau_v, 2)
        cap_a, cap_b = d.fanout(cap_v, 2)
        passes = d.op(d.op(score, "<", tau_a), "=", 0)

        def reject(b, pairs_w, def_w, stg_w, u_w, v_w, cap_w):
            b.erase(u_w, v_w, cap_w)
            return pairs_w, def_w, stg_w

        def accept(b, cm_val, pairs_w, def_w, stg_w, u_w, v_w, cap_w):
            b.erase(cm_val)
            stg_a, stg_b = b.fanout(stg_w, 2)
            can_stage = b.op(stg_a, "<", cap_w)

            def do_stage(b2, cond2, pw2, dw2, sw2, uw2, vw2):
                b2.erase(cond2)
                new_pairs = b2.cons((uw2, vw2), pw2)
                return new_pairs, dw2, b2.op(sw2, "+", 1)

            def do_defer(b2, pw2, dw2, sw2, uw2, vw2):
                b2.erase(uw2, vw2)
                return pw2, b2.op(dw2, "+", 1), sw2

            return b.branch(can_stage, do_defer, do_stage, pairs_w, def_w, stg_b, u_w, v_w)

        final_pairs, final_def, final_stg = d.branch(passes, reject, accept, pairs, deferred_cnt, staged_cnt, u, v, cap_a)
        return tau_b, cap_b, final_pairs, final_def, final_stg

    def fin(d, tau_v, cap_v, pairs, deferred_cnt, staged_cnt):
        d.erase(tau_v, cap_v, staged_cnt)
        result = (pairs, deferred_cnt)
        return result

    walker = P.stream("w", step, fin,
                     state=[("tau", NUM), ("cap", NUM), ("pairs", LIST(TUP(NUM, NUM))),
                           ("deferred", NUM), ("staged", NUM)],
                     elem=WEDGE)

    staged_list, deferred_count = d.call(walker, list=cands, init=(tau, cap, d.nil(), 0, 0))
    return staged_list, deferred_count

P.prog("t5_decide_stage_cap", prog)
P.write(os.path.join(D, "net.hvm"))
print("BUILD OK")
